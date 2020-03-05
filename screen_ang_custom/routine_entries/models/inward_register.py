# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api
from odoo import SUPERUSER_ID


class InwardRegister(models.Model):
    _name = 'inward.register'
    _description = 'Inward Register'
    _inherit = ['mail.thread']
    _order = 'name desc, date desc'

    @api.multi
    def _data_get(self):
        if self._context is None:
            context = {}
        result = {}
        location = self.env['ir.config_parameter'].get_param('ir_attachment.location')
        bin_size = self._context.get('bin_size')
        for attach in self:
            if location and attach.store_fname:
                result[attach.id] = self._file_read(location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    @api.multi
    def _data_set(self, name, value):
        # We dont handle setting data to null
        if not value:
            return True
        if self._context is None:
            context = {}
        location = self.env['ir.config_parameter'].get_param('ir_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            # attach = self.browse(cr, uid, id, context=context)
            if self.store_fname:
                self._file_delete(location, self.store_fname)
            fname = self._file_write(location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(InwardRegister, self).write(SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(InwardRegister, self).write(SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    @api.multi
    def _get_related_tasks(self):
        return (('0','Select...'))

    @api.multi
    def _get_employees(self):
        if self._context is None:
            context = {}
        emps = self.env['hr.employee'].search([])
#        usrs = self.env['hr.employee'].read(emps, ['user_id'])
        users = []
        for emp in emps: 
            if emp.user_id:
                users.append(emp.user_id)
        parts = self.env['res.users'].read(users, ['partner_id'])
        partners = []
        for part in parts:            
            partners.append(part['partner_id'][0])
        partner_obj = self.env['res.partner']
        return partner_obj.name_get(partners, context) + [(False, '')]

    @api.multi
    def _get_location(self):
        result = {}
        for line in self.env['case.sheet'].browse(self.ids):
            for court in line.court_proceedings:
                result[court.id] = line.ho_branch_id.id
        return result.keys()

    @api.multi
    def _get_default_ho_branch(self):
        emps = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        if len(emps):
            # emp = self.env['hr.employee'].browse(emps[0])
            for emp in emps:
                if emp.ho_branch_id:
                    return emp.ho_branch_id.id
        return False            

    name= fields.Char('Entry Number', size=64, required=False, readonly=False)
    date=fields.Date('Entry Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    file_number=fields.Many2one('case.sheet','File Number')
    our_ref_no=fields.Char('Our Ref. Number',size=128)
    their_number=fields.Char('Their Number',size=128)
    inward_date=fields.Date('Inward Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    agency_from=fields.Many2one('res.partner','Agency From')
    priority=fields.Selection([('low','Low'),('medium','Medium'),('high','High')],'Priority')
    assignee_id=fields.Many2one('hr.employee','Assignee',readonly=True)
    material_code=fields.Char('Material ID',readonly=True)
    material_id=fields.Many2one('material.master', 'Material Title')
    task_present=fields.Boolean('Task Present')
    assign_date=fields.Date('Assign Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    filing_date=fields.Date('Filing Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    exec_date=fields.Date('Execution Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    remarks=fields.Text('Remarks')
    task_date=fields.Date('Task Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    task_id=fields.Many2one('case.tasks.line','Related Task')
    datas= fields.Binary(compute='_data_get', fnct_inv=_data_set, string='File Content')
    datas_fname= fields.Char('File Name',size=256)
    store_fname=fields.Char('Stored Filename', size=256)
    db_datas= fields.Binary('Database Data')
    file_size=fields.Integer('File Size')
    attach_id= fields.Many2one('ir.attachment','Attachment ID')
#    addressee_name=fields.Selection(compute='_get_employees',string='Given To')
    ho_branch_id=fields.Many2one('ho.branch','Location', default=lambda s:s._get_default_ho_branch())

        

    @api.model
    def default_get(self, fields_list):
        if not self._context:
            context = {}
        res = super(InwardRegister, self).default_get(fields_list)
        return res

    @api.onchange('file_number')
    def onchange_file_number(self):
        res = {}
        if self.file_number:
            # case = self.env['case.sheet'].browse(self.file_number)
            case = self.file_number
            res['assignee_id']=(case.assignee_id and case.assignee_id.id or False)
            res['task_id']=False
        else:
            res['assignee_id' ] = False
        return {'value': res}

    @api.onchange('material_id')
    def onchange_material_title(self):
        res = {}
        if self.material_id:
            # mate = self.env['material.master'].browse(self.material_id)
            mate = self.material_id
            res['material_code']=(mate.material_code and mate.material_code or False)
        return {'value': res}

    @api.onchange('task_present')
    def onchange_task_present(self):
        res = {}
        if not self.task_present:
            res['task_date']= time.strftime('%Y-%m-%d')
            res['task_id']=False
        return {'value': res}
        
    @api.model
    def create(self, vals):
        if not 'name' in vals or not vals['name']:
            name = self.env['ir.sequence'].get('inward.register') or '/'
            vals['name'] = name
        if vals['file_number']:
            case = self.env['case.sheet'].browse(vals['file_number'])
            assignee_id = (case.assignee_id and case.assignee_id.id or False)
            vals['assignee_id'] = assignee_id
        if vals['material_id']:
            mate = self.env['material.master'].browse(vals['material_id'])
            vals['material_code']=(mate.material_code and mate.material_code or False)
        retvals = super(InwardRegister, self).create(vals)
        obj = self.browse(retvals)
        if vals['datas_fname']:
            attach_id = self.env['ir.attachment'].create({'name':vals['datas_fname'],'type':'binary','datas':vals['datas'],'user_id':self.env.user.id,'res_model':(obj.file_number and 'case.sheet' or 'inward.register'),'res_id':(obj.file_number and obj.file_number.id or retvals),'res_name':(obj.file_number and obj.file_number.name or obj.name)})
            # self.write([retvals], {'attach_id':attach_id})
            retvals.write({'attach_id':attach_id})
        return retvals

    @api.multi
    def write(self, vals):
        if 'file_number' in vals and vals['file_number']:
            case = self.env['case.sheet'].browse(vals['file_number'])
            assignee_id = (case.assignee_id and case.assignee_id.id or False)
            vals['assignee_id'] = assignee_id
        retvals = super(InwardRegister, self).write(vals)
        line = self.browse(self.id)
        if not line.attach_id and 'datas_fname' in vals:
            attach_id = self.env['ir.attachment'].create({'name':line.datas_fname,'type':'binary','datas':line.datas,'user_id':self.env.user.id,'res_model':(line.file_number and 'case.sheet' or 'inward.register'),'res_id':(line.file_number and line.file_number.id or retvals),'res_name':(line.file_number and line.file_number.name or line.name)})
            # self.write([line.id], {'attach_id':attach_id})
            line.write({'attach_id':attach_id})
        return retvals
        
InwardRegister()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: