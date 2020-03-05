# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError

import base64
import codecs
import csv
import io

Fields = ['Name']

class ConsolidatedBulkCaseSheet(models.TransientModel):
    _name = 'consolidated.bulk.case.sheet'
    _description = 'Consolidated Bulk Case Sheet'
    _inherit = ['mail.thread']

    @api.multi
    def _data_get(self):
        if self._context is None:
            context = {}
        else:
            context=self._context.copy()
        result = {}
        location = self.env['ir.config_parameter'].get_param('ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self:
            if location and attach.store_fname:                
                self.datas= self._file_read(location, attach.store_fname, bin_size)
            else:
                self.datas = attach.db_datas
        # return result

    @api.multi
    def _data_set(self):
        # We dont handle setting data to null
        if not self.datas:
            return True
        if self._context is None:
            context = {}
        location = self.env['ir.config_parameter'].get_param('ir_attachment.location')
        file_size = len(self.datas)
        if location:
            attach = self
            if attach.store_fname:
                self._file_delete(location, attach.store_fname)
            fname = self._file_write(location, self.datas)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            self.write({'store_fname': fname, 'file_size': file_size})
        else:
            self.write({'db_datas': self.datas, 'file_size': file_size})
        return True

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return res
        for line in self:
            res.append((line.id,line.name.name))
        return res

    name= fields.Many2one('case.sheet','File Number to Duplicate')
    flg_first_row=fields.Boolean('The first row of the file contains the label of the column')
    field_delimiter=fields.Selection([(',',','),(';',';'),(':',':')],'Field Delimiter', default=',')
    text_delimiter=fields.Selection([('"','"'),("'","'")],'Text Delimiter', default='"')
    datas= fields.Binary(compute='_data_get', inverse= _data_set, string='File Content')
    # datas= fields.Binary(compute='_data_get', string='File Content')
    datas_fname= fields.Char('File Content',size=256, required=True)
    store_fname= fields.Char('Stored Filename', size=256)
    db_datas= fields.Binary('Database Data')
    file_size= fields.Integer('File Size')
    attach_id= fields.Many2one('ir.attachment','Attachment ID')

    # _defaults = {
    #             'field_delimiter':',',
    #             'text_delimiter':'"',
    # }
    @api.multi
    def update_consolidated_bill_casesheet(self):
        cons_bill_obj=self.env['consolidated.bill']
        for line in self:
            case_ids = []
            _reader = codecs.getreader('utf-8')

            data = csv.reader(_reader(io.BytesIO(base64.b64decode(line.datas))), quotechar=line.text_delimiter, delimiter=line.field_delimiter)
            if self.flg_first_row is True:
                fields = next(data)
            else:
                fields = Fields
            data_lines = []
            for row in data:
                if ''.join(row).strip():
                    items = dict(zip(fields, row))
                    data_lines.append(items)
            for data in data_lines:
                name=data['Name']
                refsearchids = self.env['case.sheet'].search([('name','=',name),('client_id','=',self._context['client_id']),('work_type','=',self._context['work_type']),('casetype_id','=',self._context['casetype_id'])])

                if not len(refsearchids):
                    raise UserError(_('File Number "%s" is NOT present in the selected Client Case Details.'%name))
                else:
                    case_ids.append(refsearchids[0])
            if len(case_ids):                
                for case_id in case_ids:
                    acts=cons_bill_obj.browse(self._context['active_ids'])
                    acts.write({'case_sheet_ids':[(4,case_id.id)]})
        return True

    # @api.model
    # def create(self, vals):
    #     if self._context is None:
    #         context = {}
    #     retvals = super(ConsolidatedBulkCaseSheet, self).create(vals)
    #     return retvals
        
ConsolidatedBulkCaseSheet()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: