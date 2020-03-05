# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from odoo import fields, models, api
from odoo import SUPERUSER_ID


class AcknowledgementStatus(models.Model):
    _name = 'acknowledgement.status'

    name=fields.Char('Status Name',size=128, required=True)


class OutwardToname(models.Model):
    _name = 'outward.toname'

    outward_id=fields.Many2one('outward.register','Outward Register Ref')
    acknowledgement_status=fields.Many2one('acknowledgement.status','Status')
    name=fields.Char('To',required=True)
    from_name=fields.Char('From')
    ack_reference= fields.Char('ACK Reference',  size=128)

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return res
        for line in self:
            res.append((line.id,line.name.name))
        return res

OutwardToname()


class OutwardRegister(models.Model):
    _name = 'outward.register'
    _description = 'Outward Register'
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
            super(OutwardRegister, self).write(SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size})
        else:
            super(OutwardRegister, self).write(SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size})
        return True

    @api.multi
    def _get_to_names(self):
        res = {}
        for reg in self:
            names=''
            for line in reg.to_ids:
                names = (names!='' and (names+', '+ line.name) or line.name)
            res[reg.id] = names    
        return res

    @api.multi
    def _get_to_name_acknowledge(self, field):
        res = {}
        for reg in self:
            names=''
            for line in reg.to_ids:
                names = (names!='' and (names+', '+ (line.name + ' - ' + (line.acknowledgement_status.name or ''))) or (line.name + ' - ' + (line.acknowledgement_status.name or '')))
            res[reg.id] = names    
        return res

    @api.multi
    def _get_remainder_date(self):
        res = {}
        for reg in self:
            remaind = False
            if reg.set_remainder and reg.days_ahead and reg.days_ahead > 0:
                remaind = (datetime.strptime(reg.date, '%Y-%m-%d') + timedelta(days=reg.days_ahead)).strftime('%Y-%m-%d')
            res[reg.id] = remaind
       
        return res

    @api.multi
    def _fnct_search(self, obj,args, name):
        toname_ids = self.env['outward.toname'].search([('name','ilike',args[0][2])])
        lst = list(set([toname.outward_id.id for toname in self.env['outward.toname'].browse(toname_ids)]))
        return [('id','in',lst)]          
        
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
            for emp in emps:
                # emp = self.env['hr.employee'].browse(emps[0])
                if emp.ho_branch_id:
                    return emp.ho_branch_id.id
        return False         

    name= fields.Char('Entry Number', size=64, required=False)
    date=fields.Date('Entry Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    file_number=fields.Many2one('case.sheet','File Number')
    description=fields.Char('Description')
    auto_ref_no=fields.Boolean('Auto Ref. No')
    file_ref_no=fields.Char('Ref. No',size=128)
    material_code=fields.Char('Material ID',readonly=True)
    material_id=fields.Many2one('material.master', 'Material Title')
    to_ids=fields.One2many('outward.toname','outward_id','To Name(s)')
    assignee_id=fields.Many2one('hr.employee','Assignee',readonly=True)
    delivery_mode=fields.Many2one('delivery.master','Delivery Mode')
    party_receipt_date=fields.Date('Date of Receipt by Party', default=lambda *a: time.strftime('%Y-%m-%d'))
    inward_date=fields.Date('Inward Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    set_remainder=fields.Boolean('Set Reminder', default=True)
    days_ahead=fields.Integer('Days Ahead')
    remainder_date = fields.Date(compute='_get_remainder_date', string='Remainder Date', store=True)
    acknowledgement=fields.Char('Acknowledgement',size=128)
    datas= fields.Binary(compute='_data_get', fnct_inv=_data_set, string='File Content')
    datas_fname= fields.Char('File Name',size=256)
    store_fname= fields.Char('Stored Filename', size=256)
    db_datas= fields.Binary('Database Data')
    file_size= fields.Integer('File Size')
    attach_id= fields.Many2one('ir.attachment','Attachment ID')
    to_names=fields.Char(compute='_get_to_names',string='To Name(s)',fnct_search=_fnct_search)
    to_name_acknowledge=fields.Char(compute='_get_to_name_acknowledge',string='To Name(s) Acknowledgement')
    ho_branch_id=fields.Many2one('ho.branch','Location', default=lambda s:s._get_default_ho_branch())
    remarks=fields.Text('Remarks')
    received_date = fields.Datetime("Received Date", default=fields.Datetime.now)
    received_proof = fields.Binary(string='Received Proof')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('dispatch', 'Dispatched'),
        ('receive', 'Received'),
        ('done', 'Done')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

        
    # _defaults = {
    # 	'date':lambda *a: time.strftime('%Y-%m-%d'),
    # 	'inward_date':lambda *a: time.strftime('%Y-%m-%d'),
    # 	'party_receipt_date':lambda *a: time.strftime('%Y-%m-%d'),
    # 	'state':'new',
    # 	'ho_branch_id':lambda s, cr, uid, c:s._get_default_ho_branch(cr, uid, c),
    # }

    @api.multi
    def action_dispatch(self):
        self.write({'state': 'dispatch'})

    @api.multi
    def action_receive(self):
        self.write({'state': 'receive'})

    @api.multi
    def complete_outward(self):
        self.write({'state': 'done'})

    # @api.onchange('fileno')
    # def onchange_file_number(self, cr, uid, ids, autoref, name, , context=None):
    #     res = {}
    #
    #     if fileno:
    #         to_ids = []
    #         case = self.pool.get('case.sheet').browse(cr, uid, fileno, context=context)
    #         res['assignee_id']=(case.assignee_id and case.assignee_id.id or False)
    #         for ln in case.opp_parties:
    #             to_ids.append((0,0,{'name':ln.name}))
    #         res['to_ids'] = to_ids
    #     else:
    #         res['assignee_id' ] = False
    #         res['to_ids'] = []
    #     return {'value': res}
    #
    #     if autoref:
    #         case = self.pool.get('case.sheet').browse(cr, uid, fileno, context=context)
    #         res['file_ref_no'] = name +'/'+ (fileno and case.name +'/' or '')+ time.strftime('%Y')[2:]
    #
    #     return {'value': res}
    #
    # def onchange_material_title(self, cr, uid, ids, material, context=None):
    #     res = {}
    #     if material:
    #         mate = self.pool.get('material.master').browse(cr, uid, material, context=context)
    #         res['material_code']=(mate.material_code and mate.material_code or False)
    #     return {'value': res}
    #
    # def onchange_task_present(self, cr, uid, ids, present, context=None):
    #     res = {}
    #     if not present:
    #         res['task_date']= time.strftime('%Y-%m-%d')
    #         res['task_id']=False
    #     return {'value': res}
    #
    # def onchange_remainder(self, cr, uid, ids, remainder, context=None):
    #     res = {}
    #     if not remainder:
    #         res['days_ahead']= False
    #         res['remainder_date']= False
    #     return {'value': res}
    #
    @api.multi
    def generate_file_ref_no(self,autoref, name, fileno):
        res = {}
        if autoref:
            case = self.env['case.sheet'].browse(fileno)
            res['file_ref_no'] = name +'/'+ (fileno and case.name +'/' or '')+ time.strftime('%Y')[2:]
        else:
            res['file_ref_no'] = False
        return {'value':res}

    @api.model
    def create(self,vals):
        if not 'name' in vals or not vals['name']:
            name = self.env['ir.sequence'].get('outward.register') or '/'
            vals['name'] = name
        
        if vals['file_number']:
            case = self.env['case.sheet'].browse(vals['file_number'])
            assignee_id = (case.assignee_id and case.assignee_id.id or False)
            vals['assignee_id'] = assignee_id
        if vals['material_id']:
            mate = self.env['material.master'].browse(vals['material_id'])
            vals['material_code']=(mate.material_code and mate.material_code or False)

        retvals = super(OutwardRegister, self).create(vals)
        obj = self.browse(retvals)

        if vals['datas_fname']:            
            attach_id = self.env['ir.attachment'].create({'name':vals['datas_fname'],'type':'binary','datas':vals['datas'],'res_model':(obj.file_number and 'case.sheet' or 'outward.register'),'res_id':(obj.file_number and obj.file_number.id or retvals),'res_name':(obj.file_number and obj.file_number.name or obj.name)})
            # self.write(cr, uid, [retvals], {'attach_id':attach_id})
            retvals.write({'attach_id':attach_id})
        return retvals        

    @api.multi
    def write(self, vals):
        if 'file_number' in vals and vals['file_number']:
            case = self.env['case.sheet'].browse(vals['file_number'])
            assignee_id = (case.assignee_id and case.assignee_id.id or False)
            vals['assignee_id'] = assignee_id
        
        retvals = super(OutwardRegister, self).write(vals)
        line = self.browse(self.ids[0])
        if not line.attach_id and 'datas_fname' in vals:
            attach_id = self.env['ir.attachment'].create({'name':line.datas_fname,'type':'binary','datas':line.datas,'res_model':'outward.register','res_id':line.id,'res_name':line.name})
            line.write({'attach_id':attach_id.id})
        return retvals
