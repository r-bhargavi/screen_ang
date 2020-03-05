# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class CaseCancel(models.TransientModel):

    _name = "case.cancel"
    _description = "Cancel Case Sheet"

    name= fields.Text('Reason')
    cancel_date=fields.Date('Cancel Date', default=lambda *a: time.strftime('%Y-%m-%d'))

    # _defaults = {
    #     'cancel_date':lambda *a: time.strftime('%Y-%m-%d'),
    # }

    @api.multi
    def cancel_case_sheet(self):
        if self._context is None:
            context = {}
        case_id = self.env['case.sheet'].browse(self.env.context.get('active_id', False))
        if case_id:
            # self.env['project.project'].set_cancel([case_id.project_id.id])
            type_ids = self.env['project.task.type'].search([('state', '=', 'cancelled')])
            if type_ids:
                self.env.cr.execute("update project_task set state='cancel', stage_id=%s  where project_id=%s;",
                                    (type_ids[0].id, case_id.project_id.id))

        invoice_ids = self.env['account.invoice'].search([('case_id', '=', case_id.id)])
        for inv_obj in invoice_ids:
            if inv_obj.state != 'cancel':
                raise UserError(_('Please cancel the invoices related to this case sheet!'))
        return case_id.write(
            {'state': 'cancel', 'cancel_comments': self.name, 'cancel_date': self.cancel_date})
        # case_id = self._context.get('active_id', False)
        # for case_obj in self.env['case.sheet'].browse([case_id]):
        #     self.env['project.project'].set_cancel([case_obj.project_id.id])
        #     type_ids = self.env['project.task.type'].search([('state', '=', 'cancelled')])
        #     if type_ids:
        #         self.env.cr.execute("update project_task set state='cancel', stage_id=%s  where project_id=%s;",(type_ids[0], case_obj.project_id.id))
        #
        # invoice_ids = self.env['account.invoice'].search([('case_id', '=', case_id)])
        # for inv_obj in self.env['account.invoice'].browse(invoice_ids):
        #     if inv_obj.state != 'cancel':
        #         raise UserError(_('Warning!'),_('Please cancel the invoices related to this case sheet!'))
        # # return self.pool.get('case.sheet').write(cr, uid, [case_id], {'state':'cancel','cancel_comments':context['comments'],'cancel_date':context['cancel_date']})
        # return case_id.write({'state':'cancel','cancel_comments':context['comments'],'cancel_date':context['cancel_date']})

CaseCancel()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: