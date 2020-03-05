# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('name')
    def onchange_name(self):
        if not self.name:
            return {'value': {'client_data_id': False}}
        val = {
            'client_data_id': (self.name and len(self.name.replace(" ",""))>=4 and self.name.replace(" ","")[:4].upper() or False)
        }
        return {'value': val}

    client_data_id= fields.Char('Client ID',size=10)
    pan=fields.Char('PAN',size=50)
    client_branch= fields.Char('Location/Division',size=40)
    extension=fields.Char('Extension',size=10)
    company_parent_id= fields.Many2one('res.partner', 'Parent Company')
    opposite=fields.Boolean('Opposite Party')
    district_id=fields.Many2one('district.district', 'District')
    property_account_payable=fields.Many2one('account.account',string="Account Payable", domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner")
    property_account_receivable= fields.Many2one('account.account', string="Account Receivable",domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner")
    associate= fields.Boolean('Associate')
    supplier_code= fields.Char('Supplier Code', size=128)
    create_date= fields.Datetime('Create Date', readonly=True)
    client_manager_id= fields.Many2one('hr.employee','Client Relationship Manager')
    vendor_type_option = fields.Selection([('temporary', 'Temporary'), ('permanent', 'Permanent')],
                                          string="Vendor Type")
    referral_specification = fields.Selection(
        [('matter_specific', 'Matter Specific'), ('client_specific', 'Client Specific')], string="Referral Specification")
    referral_type = fields.Selection([('ref_emp', 'Refer by Employee'), ('ref_part', 'Refer by Partner'),
                                      ('ref_ext', 'Refer by External')], string="Referral Type")
    response_person = fields.Many2one('res.partner', 'Response Person')
    response_person_emp = fields.Many2one('hr.employee', 'Response Person')
    division_id=fields.Many2one('hr.department', string='Department/Division', track_visibility='onchange', ondelete="restrict")
    assignee_id= fields.Many2one('hr.employee',string='Assignee', track_visibility='onchange')

    referral_percentage = fields.Float('Referral Percentage')
    referral_amount = fields.Float('Referral Amount')
    referral_validity = fields.Date('Referral Validity')
    ven_bank_name = fields.Char('Bank Name')
    ven_bank_branch = fields.Char('Bank Branch')
    ven_bank_ac_no = fields.Char('Bank Account Number')
    ven_bank_ifsc = fields.Char('Bank IFSC Code', size=11)
    ven_pan_card = fields.Char('Vendor Pancard', size=10)

    _sql_constraints = [
        ('uniq_vendor_pancard', 'unique (ven_pan_card)', 'Vendor pancard already exist!'),
    ]
    @api.onchange('division_id')
    def _get_assignee_id(self):
        assignee = []
        if self.division_id:
            dept = self.env['hr.department'].search([('id', '=', self.division_id.id)])
            assignee.append(dept.manager_id.id)
            return {
                'domain': {'assignee_id': [('id', 'in', assignee)]}
            }

    @api.one
    @api.constrains('ven_pan_card')
    def _uniq_vendor_pancard(self):
        if self.ven_pan_card:
            if len(self.ven_pan_card) != 10:
                raise ValidationError(_("Enter valid pancard number!"))

    @api.one
    @api.constrains('ven_bank_ifsc')
    def _uniq_vendor_bank_ifsc(self):
        if self.ven_bank_ifsc:
            if len(self.ven_bank_ifsc) != 11:
                raise ValidationError(_("Enter valid bank IFSC code!"))

    @api.model
    def create(self, vals):
        if vals.get('supplier', False) or vals.get('associate', False):
            supplier_code = self.env['ir.sequence'].next_by_code('res.partner')
            vals.update({'supplier_code': supplier_code})
        res = super(ResPartner, self).create(vals)
        return res
    
    
    def onchange_district(self, cr, uid, ids, district_id, context=None):
        if district_id:
            state_id = self.pool.get('district.district').browse(cr, uid, district_id, context).state_id.id
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id,'state_id':state_id}}
        return {}

    @api.onchange('state_id')
    def onchange_state(self):
        return {'value':{ 'district_id' : False}}

    @api.multi
    def name_get(self):
        res = []
        for line in self:
            name = False
            if line.name:
                name =line.name
            if line.supplier_code and line.supplier:
                name = (name and name + '[' + line.supplier_code + ']' or False)
            if line.client_branch:
                name += ', ' + line.client_branch
            # res.append(name)
            res.append((line.id, "%s" % (name)))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        ids = self.browse()
        if name:
            ids = self.search([('name', operator, name)] + args, limit=limit)
            if not ids:
                # ids = self.search([('supplier_code', operator, name)], limit=limit)
                ids = self.search(['|', ('name', operator, name), ('supplier_code', operator, name)] + args, limit=limit)
        else:
            ids = self.search(args, limit=limit)
        return ids.name_get()

#    @api.multi
#    def search(self, args, offset=0, limit=None, order=None,count=False):
#        if self._context is None:
#            context = {}
#        return super(ResPartner, self).search(args, offset, limit, order, count)
