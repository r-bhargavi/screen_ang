# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class SaleMakeInvoice(models.TransientModel):
    _name = "sale.make.invoice"
    _description = "Sales Make Invoice"

    grouped= fields.Boolean('Group the invoices', help='Check the box to group the invoices for the same customers', default=False)
    invoice_date= fields.Date('Invoice Date', default=fields.date.today)

    # _defaults = {
    #     'grouped': False,
    #     'invoice_date': fields.date.context_today,
    # }
    @api.multi
    def view_init(self,fields_list):
        if self._context is None:
            context = {}
        record_id = self._context and self._context.get('active_id', False)
        order = self.env['sale.order'].browse(record_id)
        if order.state == 'draft':
            raise UserError(_('Warning!'), _('You cannot create invoice when sales order is not confirmed.'))
        return False

    @api.multi
    def make_invoices(self):
        order_obj = self.env['sale.order']
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        newinv = []
        if self._context is None:
            context = {}
        data = self.read(self.ids)[0]
        for sale_order in order_obj.browse(self._context.get(('active_ids'), [])):
            if sale_order.state != 'manual':
                raise UserError(_('Warning!'), _("You shouldn't manually invoice the following sale order %s") % (sale_order.name))

        order_obj.action_invoice_create(self._context.get(('active_ids'), []), data['grouped'], date_invoice=data['invoice_date'])

        for o in order_obj.browse(self._context.get(('active_ids'), [])):
            for i in o.invoice_ids:
                newinv.append(i.id)

        result = mod_obj.get_object_reference('account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read([id])[0]
        result['domain'] = "[('id','in', [" + ','.join(map(str, newinv)) + "])]"

        return result

SaleMakeInvoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
