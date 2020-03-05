# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class CaseAdvancePaymentInv(models.TransientModel):
    _name = "case.advance.payment.inv"
    _description = "Case Advance Payment Invoice"

    @api.multi
    def _get_advance_product(self):
        try:
            product = self.env['ir.model.data'].get_object('sale', 'advance_product_0')
        except ValueError:
            # a ValueError is returned if the xml id given is not found in the table ir_model_data
            return False
        return product.id

    advance_payment_method=fields.Selection([
        ('all', 'Invoice the whole Case'),
        ('fixed','Fixed price (deposit)'),
        ('task', 'Some Tasks')],string='What do you want to invoice?', required=True, default='all',
        help="""Use All to create the final invoice. Use Fixed Price to invoice a specific amound in advance. Use Some Tasks to invoice a selection of the Tasks.""")
    qtty= fields.Float('Quantity', digits=(16, 2), required=True, default=1.0)
    product_id=fields.Many2one('product.product', 'Advance Product',help="""Select a product of type service which is called 'Advance Product'.You may have to create it and set it as a default value on this field.""", default='_get_advance_product')
    amount= fields.Float('Advance Amount', digits_compute= dp.get_precision('Account'), help="The amount to be invoiced in advance.")
    #
    # _defaults = {
    #     'advance_payment_method': 'all',
    #     'qtty': 1.0,
    #     'product_id': _get_advance_product,
    # }
    @api.onchange('advance_payment_method','product_id')
    def onchange_method(self):
        if self.advance_payment_method == 'percentage':
            return {'value': {'amount':0, 'product_id':False }}
        if self.product_id:
            product = self.env['product.product'].browse(self.product_id)
            return {'value': {'amount': product.list_price}}
        return {'value': {'amount': 0}}

    @api.multi
    def _prepare_advance_invoice_vals(self):
        if self._context is None:
            context = {}
        sale_obj = self.env['sale.order']
        ir_property_obj = self.env['ir.property']
        fiscal_obj = self.env['account.fiscal.position']
        inv_line_obj = self.env['account.invoice.line']
        wizard = self.browse(self.ids[0])
        sale_ids = self._context.get('active_ids', [])

        result = []
        for sale in sale_obj.browse(sale_ids):
            val = inv_line_obj.product_id_change([], wizard.product_id.id,uom_id=False, partner_id=sale.partner_id.id, fposition_id=sale.fiscal_position.id)
            res = val['value']

            # determine and check income account
            if not wizard.product_id.id :
                prop = ir_property_obj.get('property_account_income_categ', 'product.category')
                prop_id = prop and prop.id or False
                account_id = fiscal_obj.map_account(sale.fiscal_position or False, prop_id)
                if not account_id:
                    raise UserError(_('Configuration Error!'),_('There is no income account defined as global property.'))
                res['account_id'] = account_id
            if not res.get('account_id'):
                raise UserError(_('Configuration Error!'),_('There is no income account defined for this product: "%s" (id:%d).') % (wizard.product_id.name, wizard.product_id.id,))

            # determine invoice amount
            if wizard.amount <= 0.00:
                raise UserError(_('Incorrect Data'),_('The value of Advance Amount must be positive.'))
            if wizard.advance_payment_method == 'percentage':
                inv_amount = sale.amount_total * wizard.amount / 100
                if not res.get('name'):
                    res['name'] = _("Advance of %s %%") % (wizard.amount)
            else:
                inv_amount = wizard.amount
                if not res.get('name'):
                    #TODO: should find a way to call formatLang() from rml_parse
                    symbol = sale.pricelist_id.currency_id.symbol
                    if sale.pricelist_id.currency_id.position == 'after':
                        res['name'] = _("Advance of %s %s") % (inv_amount, symbol)
                    else:
                        res['name'] = _("Advance of %s %s") % (symbol, inv_amount)

            # determine taxes
            if res.get('invoice_line_tax_id'):
                res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
            else:
                res['invoice_line_tax_id'] = False

            # create the invoice
            inv_line_values = {
                'name': res.get('name'),
                'origin': sale.name,
                'account_id': res['account_id'],
                'price_unit': inv_amount,
                'quantity': wizard.qtty or 1.0,
                'discount': False,
                'uos_id': res.get('uos_id', False),
                'product_id': wizard.product_id.id,
                'invoice_line_tax_id': res.get('invoice_line_tax_id'),
                'account_analytic_id': sale.project_id.id or False,
            }
            inv_values = {
                'name': sale.client_order_ref or sale.name,
                'origin': sale.name,
                'type': 'out_invoice',
                'reference': False,
                'account_id': sale.partner_id.property_account_receivable.id,
                'partner_id': sale.partner_invoice_id.id,
                'invoice_line': [(0, 0, inv_line_values)],
                'currency_id': sale.pricelist_id.currency_id.id,
                'comment': '',
                'payment_term': sale.payment_term.id,
                'fiscal_position': sale.fiscal_position.id or sale.partner_id.property_account_position.id
            }
            result.append((sale.id, inv_values))
        return result

    @api.multi
    def _create_invoices(self, inv_values, case_id):
        inv_obj = self.env['account.invoice']
        case_obj = self.env['case.sheet']
        inv_id = inv_obj.create(inv_values)
        inv_obj.button_reset_taxes([inv_id])
        # add the invoice to the sales order's invoices
        # case_obj.write(cr, uid, case_id, {'invoice_ids': [(4, inv_id)]}, context=context)
        case_obj.case_id.write({'invoice_ids': [(4, inv_id)]})
        return inv_id

    @api.multi
    def create_invoices(self, ):
        """ create invoices for the active sales orders """
        case_obj = self.env['case.sheet']
        act_window = self.env['ir.actions.act_window']
        wizard = self.browse(self.ids[0])
        case_ids = self._context.get('active_ids', [])
        if wizard.advance_payment_method == 'all':
            # create the final invoices
            res = case_obj.manual_invoice(case_ids)
            if self._context.get('open_invoices', False):
                return res
            return {'type': 'ir.actions.act_window_close'}

        if wizard.advance_payment_method == 'lines':
            # open the list view of sales order lines to invoice
            res = act_window.for_xml_id('sale', 'action_order_line_tree2')
            res['context'] = {
                'search_default_uninvoiced': 1,
                # 'search_default_order_id': sale_ids and sale_ids[0] or False,
            }
            return res
        assert wizard.advance_payment_method in ('fixed', 'percentage')

        inv_ids = []
        for sale_id, inv_values in self._prepare_advance_invoice_vals():
            inv_ids.append(self._create_invoices(inv_values, sale_id))

        if self._context.get('open_invoices', False):
            return self.open_invoices(inv_ids)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def open_invoices(self,invoice_ids):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference('account', 'invoice_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference('account', 'invoice_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Advance Invoice'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': invoice_ids[0],
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': "{'type': 'out_invoice'}",
            'type': 'ir.actions.act_window',
        }

CaseAdvancePaymentInv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
