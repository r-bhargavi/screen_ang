# -*- coding: utf-8 -*-
import time
import re
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
from odoo import netsvc
import base64


class BulkCaseHold(models.TransientModel):
    _name = 'bulk.case.hold'
    _description = 'Bulk Case Hold/Unhold'
    

    datas= fields.Binary('File Content')
    summary= fields.Text('Summary')
    type= fields.Selection([('hold', 'Hold'), ('unhold', 'Unhold')], 'Type', default='hold')

    # _defaults = {
    #     'type': 'hold'
    #     }
    @api.multi
    def generate_bulk_casesheet_hold(self):
        if self._context is None:
            context = {}
        case_pool = self.env['case.sheet']
        # wf_service = netsvc.LocalService("workflow")
        ir_pool = view_ref = self.env['ir.model.data']
        summary = ''
        for line in self:
            csvfile = base64.b64decode(line.datas)
            # csvfile = line.datas.decode('base64')
            rowcount = 0
            csvsplit = csvfile.split()
            # csvsplit = csvfile.split('\n')
            case_sheet =[row.strip() for row in csvsplit if row]
            case_ids = case_pool.search([('name', 'in', case_sheet),('state', 'not in', ['new', 'done', 'cancel'])])
            if case_ids:
                if line.type == 'hold':
                    type_ids = self.env['project.task.type'].search([('state', '=', 'hold')])
                    for case_obj in case_ids:
                        self.env.cr.execute("update project_task set state='hold', stage_id=%s  where project_id=%s and state in ('draft','pending', 'open');",(type_ids[0].id, case_obj.project_id.id))
                    # case_pool.write(cr, uid, case_ids, {'state': 'hold'}, context=context)
                        case_obj.write({'state': 'hold'})
                else:
                    type_ids = self.env['project.task.type'].search([('state', '=', 'open')])
                    for case_obj in case_ids:
                        self.env.cr.execute("update project_task set state='open', stage_id=%s  where project_id=%s and state in ('hold');",(type_ids[0].id, case_obj.project_id.id))

                    # case_pool.write(cr, uid, case_ids, {'state':'inprogress'}, context=context)
                        case_obj.write({'state':'inprogress'})
        view_id = False
        
        view_ref = ir_pool.get_object_reference('legal_e', 'bulk_case_hold_form_closed')
        view_id = view_ref and view_ref[1] or False,
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Case Sheet Hold'),
            'res_model': 'bulk.case.hold',
            'res_id': self.ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            }
        
BulkCaseHold()
