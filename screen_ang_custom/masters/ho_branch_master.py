# -*- coding: utf-8 -*-
from odoo import fields, models, api

        
class HoBranch(models.Model):
    _name = 'ho.branch'
    _description = "Head Office"

    @api.multi
    def _public_holiday_count(self):
        for record in self:
            record.public_holiday_count = self.env['ho.holidays.public.line'].search_count(
                [('office_id', '=', record.id)])

    @api.multi
    def _weekly_holiday_count(self):
        for record in self:
            record.weekly_holiday_count = self.env['ho.holidays.weekly.line'].search_count(
                [('office_id', '=', record.id)])

    @api.multi
    def _total_holiday_count(self):
        for record in self:
            if record.public_holiday_count or record.weekly_holiday_count:
                record.total_holiday_count = record.public_holiday_count + record.weekly_holiday_count

    state_id= fields.Many2one('res.country.state', 'State', required=True)
    name= fields.Char('Office Name', size=64, required=True)
    code= fields.Char('Office Code', size=10, required=True)
    sequence_id= fields.Many2one('ir.sequence', 'Entry Sequence', help="This field contains the information related to the numbering of the Case Entries.")
    district_id=fields.Many2one('district.district', 'District')
    country_id=fields.Many2one('res.country', 'Country')
    street=fields.Char('Street')
    street2=fields.Char('Street 2')
    zip=fields.Char('zip')
    phone=fields.Char('Phone')
    mobile=fields.Char('Mobile')
    email=fields.Char('E-mail')
    city=fields.Char('City')
    active=fields.Boolean('Active')
    client_service_executive_id=fields.Many2one('hr.employee', string='Client Service Manager', track_visibility='onchange')
    no_yearly_leave = fields.Integer('Number of Yearly Leave')
    calendar_year = fields.Char('Calendar Year', required=True)
    public_line_ids = fields.One2many('ho.holidays.public.line', 'office_id', 'Public Holidays')
    weekly_line_ids = fields.One2many('ho.holidays.weekly.line', 'office_id', 'Weekly Holidays')
    public_holiday_count = fields.Integer(compute='_public_holiday_count', string='Total Public Holidays')
    weekly_holiday_count = fields.Integer(compute='_weekly_holiday_count', string='Total Weekly Holidays')
    total_holiday_count = fields.Integer(compute='_total_holiday_count', string='Total Holidays')

    # district set as null when no state present
    @api.onchange('state_id')
    def onchange_state(self):
        return {'value': {'district_id': False}}
    
    # state set as null when no country preset
    @api.onchange('country_id')
    def onchange_country(self):
        return {'value': {'state_id': False}}

    @api.model
    def create_sequence(self,vals):
        """ Create new no_gap entry sequence for every new Branch
        """
        seq = {
            'name': vals['name'],
            'implementation': 'no_gap',
            'padding': 3,
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        return self.env['ir.sequence'].create(seq)

    @api.model
    def create(self, vals):
        if vals is None:
           vals = {}
        vals.update({'sequence_id': False})
        return super(HoBranch, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(HoBranch, self).write(vals)
        # set remaining leaves in HR employee form
        if vals.get('no_yearly_leave'):
            employee_ids = self.env['hr.employee'].search([('ho_branch_id', '=', self.id)])
            for employee in employee_ids:
                employee.write({'remaining_leaves': vals.get('no_yearly_leave')})
        return res


class HoHolidaysPublicLine(models.Model):

    _name = 'ho.holidays.public.line'
    _description = 'Public Holiday Lines'
    _order = "date, name desc"

    name = fields.Char('Name', size=128, required=True)
    date = fields.Date('Date', required=True)
    office_id = fields.Many2one('ho.branch', 'Office Calendar Year')


class HoHolidaysWeeklyLine(models.Model):

    _name = 'ho.holidays.weekly.line'
    _description = 'Weekly Holiday Lines'
    _order = "date, name desc"

    name = fields.Char('Name', size=128, required=True)
    date = fields.Date('Date', required=True)
    office_id = fields.Many2one('ho.branch', 'Office Calendar Year')
