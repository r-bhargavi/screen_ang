# -*- coding: utf-8 -*-
from odoo import fields, models, api


class JobSheetMaster(models.Model):
    _name = 'job.sheet.master'
    #COMPANY DETAILS
    company_name=fields.Many2one('res.partner', 'Company Name')
    company_code= fields.Char('Company Code',size=128, required=True)
    company_address=fields.Char('Address' ,required=True)
    job_sheet_number=fields.Char('Job Sheet Ref')
    #CONTACT PERSON DETAILS
    name=fields.Many2one('res.partner', 'Name')
    designation= fields.Char('Designation',size=128, required=True)
    contact_no= fields.Char('Contact No',size=128, required=True)
    email_id= fields.Char('Email ID',size=128, required=True)
    #COMPANY BRANCH DETAILS
    branch_name= fields.Char('Branch Name', size=128)
    branch_code= fields.Char('Branch Code', size=128)
    branch_type=fields.Char('Branch Type', change_default=True, size=24)
    branch_address= fields.Text('Branch Address')
    #INQUIRY DETAILS
    inq_type = fields.Selection([('a', 'A'), ('b', 'B')],'Inquiry Type')
    inq_ref = fields.Selection([('a', 'A'), ('b', 'B')],'Inquiry Reference')
    branch = fields.Selection([('a', 'A'), ('b', 'B')],'Branch')
    mer_name = fields.Selection([('a', 'A'), ('b', 'B')],'Merchant Name')
    priority = fields.Selection([('a', 'A'), ('b', 'B')],'Merchant Name')
    no_of_days= fields.Char('No.Of Days', size=64)
    date_of_submission = fields.Date('Date of Submission')
    date_of_inq = fields.Date('Inquiry Date')
    inq_note= fields.Text('Inquiry Note')
    unit= fields.Char('Unit', size=64)

    @api.model
    def create(self, vals):
        if self._context is None:
            context = {}
        vals['job_sheet_number'] = self.env['ir.sequence'].get('job.sheet.master')
        retvals = super(JobSheetMaster, self).create(vals)
        return retvals

    #@api.model
    #def create(self, vals):
     #   """ Create new no_gap entry sequence for every new Branch
      #  """
       # seq = {
        #    'job_sheet_number': vals['job_sheet_number'],
         #   'implementation': 'no_gap',
          #  'padding': 3,
           # 'number_increment': 1
        #}
        #if 'company_id' in vals:
         #   seq['company_id'] = vals['company_id']
        #return self.env['ir.sequence'].create(seq)






JobSheetMaster()
