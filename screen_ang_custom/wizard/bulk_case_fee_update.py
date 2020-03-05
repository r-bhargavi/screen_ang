# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
import base64
import csv
import io
import codecs


class BulkCaseFeeUpdate(models.TransientModel):
    _name = 'bulk.case.fee.update'
    _description = 'Bulk Case Fee Update'

    flg_first_row=fields.Boolean('The first row of the file contains the label of the column', default=True)
    field_delimiter=fields.Selection([(',',','),(';',';'),(':',':')], 'Field Delimiter',default=',')
    text_delimiter=fields.Selection([('"','"'),("'","'")], 'Text Delimiter', default='"')
    datas= fields.Binary('File Content')

    @api.multi
    def generate_bulk_case_fee_update(self):
        _reader = codecs.getreader('latin-1')
        if self._context is None:
            context = {}
        case_pool = self.env['case.sheet']
        office_pool = self.env['ho.branch']
        fixed_pool = self.env['fixed.price.stages']
        case_tasks_pool = self.env['case.tasks.line']
        task_pool = self.env['task.master']
        ir_pool = self.env['ir.model.data']
        for line in self:
            data=csv.reader(_reader(io.BytesIO(base64.b64decode(line.datas))), quotechar='"', delimiter=',')
            for cells in data:
                if self.flg_first_row:
                    self.flg_first_row = False
                    continue
                if len(cells)>1:
                    case_ids = []
                    if cells[0] and cells[2] and cells[3]:
                        fixed_ids = []
                        case_ids = case_pool.search([('name', '=', cells[0])])
                        office_ids = office_pool.search([('name', '=', cells[3])])
                        tasks_ids = task_pool.search([('name', '=', cells[2])])
                        if tasks_ids and office_ids:
                            case_tasks_ids = case_tasks_pool.search([('name', '=', tasks_ids.id), ('case_id', '=', case_ids.id)], limit=1)
                            if case_tasks_ids:
                                fixed_ids = fixed_pool.search([('name', '=', case_tasks_ids.id),('office_id', '=', office_ids.id), ('case_id', '=', case_ids.id)])
                        if case_ids and fixed_ids:
                            fixed_ids.write({'amount': cells[4]})
                            case_ids.write({'fixed_price': cells[1]})
                    elif cells[2] and cells[3] and case_ids:
                        fixed_ids = []
                        office_ids = office_pool.search([('name', '=', cells[3])])
                        tasks_ids = task_pool.search([('name', '=', cells[2])])
                        if tasks_ids and office_ids:
                            case_tasks_ids = case_tasks_pool.search([('name', 'in', tasks_ids)])
                            if case_tasks_ids:
                                fixed_ids = fixed_pool.search([('name', 'in', case_tasks_ids),('office_id', '=', office_ids[0]), ('case_id', 'in', case_ids)])
                        if fixed_ids:
                            fixed_ids.write({'amount': cells[4]})
        view_id = False
        
        view_ref = ir_pool.get_object_reference('legal_e', 'bulk_case_fee_update_closed')
        view_id = view_ref and view_ref[1] or False,
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Case Fee Update'),
            'res_model': 'bulk.case.fee.update',
            'res_id': self.ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            }
