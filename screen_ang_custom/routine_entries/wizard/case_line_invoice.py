# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import netsvc
from odoo.exceptions import UserError


class SaleOrderLineMakeInvoice(models.TransientModel):
    _name = "sale.order.line.make.invoice"
    _description = "Sale OrderLine Make_invoice"

    @api.multi
    def make_invoices(self):
        """
             To make invoices.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: A dictionary which of fields with values.

        """
        if self._context is None: context = {}
        res = False
        invoices = {}

    #TODO: merge with sale.py/make_invoice
        def make_invoice(order, lines):
            """
                 To make invoices.

                 @param order:
                 @param lines:

                 @return:

            """
            a = order.partner_id.property_account_receivable.id
            if order.partner_id and order.partner_id.property_payment_term.id:
                pay_term = order.partner_id.property_payment_term.id
            else:
                pay_term = False
            inv = {
                'name': order.name,
                'origin': order.name,
                'type': 'out_invoice',
                'reference': "P%dSO%d" % (order.partner_id.id, order.id),
                'account_id': a,
                'partner_id': order.partner_invoice_id.id,
                'invoice_line': [(6, 0, lines)],
                'currency_id' : order.pricelist_id.currency_id.id,
                'comment': order.note,
                'payment_term': pay_term,
                'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
                'user_id': order.user_id and order.user_id.id or False,
                'company_id': order.company_id and order.company_id.id or False,
                'date_invoice': fields.date.today(),
            }
            inv_id = self.env['account.invoice'].create(inv)
            return inv_id

        sales_order_line_obj = self.env['sale.order.line']
        sales_order_obj = self.env['sale.order']
        # wf_service = netsvc.LocalService('workflow')
        for line in sales_order_line_obj.browse(self._context.get('active_ids', [])):
            if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
                if not line.order_id in invoices:
                    invoices[line.order_id] = []
                line_id = sales_order_line_obj.invoice_line_create([line.id])
                for lid in line_id:
                    invoices[line.order_id].append(lid)
        for order, il in invoices.items():
            res = make_invoice(order, il)
            self.env.cr.execute('INSERT INTO sale_order_invoice_rel \
                    (order_id,invoice_id) values (%s,%s)', (order.id, res))
            flag = True
            data_sale = sales_order_obj.browse(order.id)
            for line in data_sale.order_line:
                if not line.invoiced:
                    flag = False
                    break
            if flag:
                # wf_service.trg_validate(uid, 'sale.order', order.id, 'manual_invoice', cr)
                # sales_order_obj.write(cr, uid, [order.id], {'state': 'progress'})
                sales_order_line_obj.order.write({'state': 'progress'})

        if not invoices:
            raise UserError(_('Warning!'), _('Invoice cannot be created for this Sales Order Line due to one of the following reasons:\n1.The state of this sales order line is either "draft" or "cancel"!\n2.The Sales Order Line is Invoiced!'))
        if context.get('open_invoices', False):
            return self.open_invoices(res)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def open_invoices(self, invoice_ids):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference('account', 'invoice_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference('account', 'invoice_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Invoice'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': invoice_ids,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': {'type': 'out_invoice'},
            'type': 'ir.actions.act_window',
        }

SaleOrderLineMakeInvoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
