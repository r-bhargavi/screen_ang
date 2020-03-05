# -*- coding: utf-8 -*-
import time
import re
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
from odoo import netsvc
import base64


class BulkTaskClose(models.TransientModel):
    _name = 'bulk.task.close'
    _description = 'Bulk Task Close'

    flg_first_row=fields.Boolean('The first row of the file contains the label of the column', default=True)
    field_delimiter=fields.Selection([(',',','),(';',';'),(':',':')],'Field Delimiter', default=',')
    text_delimiter=fields.Selection([('"','"'),("'","'")],'Text Delimiter', default='"')
    datas= fields.Binary('File Content')

    # _defaults = {
    #     'field_delimiter':',',
    #     'text_delimiter':'"',
    #     'flg_first_row': True
    #     }
    @api.multi
    def generate_bulk_task_close(self):
        if self._context is None:
            context = {}
        task_pool = self.env['project.task']
        task_master_pool = self.env['task.master']
        project_pool = self.env['project.project']
        # wf_service = netsvc.LocalService("workflow")
        ir_pool = self.env['ir.model.data']
        stage_ids = self.env['project.task.type'].search([('state','=','done')])
        task_ids = []
        for line in self:
            csvfile = base64.b64decode(line.datas)
            # csvfile = line.datas.decode('base64')
            rowcount = 0
            csvsplit = csvfile.split()
            # csvsplit = csvfile.split('\n')
            for row in range(rowcount,len(csvsplit)):
                csvsplit[row]=re.sub(b'[^\x00-\x7f]',b'',csvsplit[row])
                cells = csvsplit[row].split(b'line.field_delimiter')
                text_delimiter = ''
                if line.text_delimiter:
                    text_delimiter = line.text_delimiter
                if len(cells)>1:
                    cells[0] = cells[0].replace(text_delimiter,"").rstrip()
                    cells[1] = cells[1].replace(text_delimiter,"").rstrip()
                    task_id = task_master_pool.search([('name', '=', cells[0])])
                    project_id = project_pool.search([('name', '=', cells[1])])
                    if task_id and project_id:
                        task_ids += task_pool.search([('name', '=', task_id[0]), ('project_id', '=', project_id[0])])
                        
        task_ids  = list(set(task_ids))
        if task_ids and stage_ids:
            # task_pool.write(cr, uid, task_ids, {'state': 'done', 'stage_id': stage_ids[0]}, context=context)
            task_pool.task_ids.write({'state': 'done', 'stage_id': stage_ids[0]})
        
        view_ref = ir_pool.get_object_reference('legal_e', 'bulk_task_close_form_closed')
        view_id = view_ref and view_ref[1] or False,
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Task Close'),
            'res_model': 'bulk.task.close',
            'res_id': self.ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            }
        
BulkTaskClose()
