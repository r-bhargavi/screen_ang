# -*- coding: utf-8 -*-
import time

from odoo import fields, models, api
from odoo.tools.translate import _
import base64


class BulkCaseClose(models.TransientModel):
    _name = 'bulk.case.close'
    _description = 'Bulk Case Close'

    datas= fields.Binary('File Content')
    summary= fields.Text('Summary')

    @api.multi
    def generate_bulk_casesheet_close(self):
        if self._context is None:
            context = {}
        case_pool = self.env['case.sheet']
        ir_pool = self.env['ir.model.data']
        summary = ''
        for line in self:
            csvfile = base64.b64decode(line.datas)
            csvsplit = csvfile.split()
            case_sheet =[row.strip() for row in csvsplit if row]
            case_ids = case_pool.search([('name', 'in', case_sheet)])
            for case_obj in case_ids:
                draft_ids =[]
                checked = False
                invoice_ids = self.env['account.invoice'].search([('case_id', '=', case_obj.id)])
                for inv_obj in invoice_ids:
                    if inv_obj.state not in ['paid', 'cancel', 'draft']:
                        if inv_obj.state == 'draft':
                            draft_ids.append(inv_obj.id)
                        else:
                            checked = True

                if not checked:
                    case_obj.project_id.with_context(case_close=True).set_done()
                    type_ids = self.env['project.task.type'].search([('state', '=', 'done')])
                    if type_ids:
                        self.env.cr.execute("update project_task set state='done', stage_id=%s  where project_id=%s;",(type_ids[0].id, case_obj.project_id.id))
                    case_obj.write({'state': 'done', 'close_date': time.strftime('%Y-%m-%d')})
                else:
                    summary += case_obj.name + '\n'

        self.write({'summary': summary})
        view_id = False
        if summary:
            view_ref = ir_pool.get_object_reference('legal_e', 'bulk_case_close_form_summary')
            view_id = view_ref and view_ref[1] or False,
        else:
            view_ref = ir_pool.get_object_reference('legal_e', 'bulk_case_close_form_closed')
            view_id = view_ref and view_ref[1] or False,
            
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Case Sheet Close'),
            'res_model': 'bulk.case.close',
            'res_id': self.ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
        }
