# -*- coding: utf-8 -*-
from odoo import fields, models, api

class AssigneeMaster(models.Model):
    _name = 'assignee.master'

    name= fields.Char('Assignee Name', size=128, required=True)
    code=fields.Char('Code', size=64, required=True)
    email= fields.Char('Email', size=240, required=True)
    phone=fields.Char('Phone', size=64, required=True)
    street= fields.Char('Street', size=128, required=True)
    street2= fields.Char('Street2', size=128)
    zip=fields.Char('Zip',size=24, required=True)
    city=fields.Char('City', size=128, required=True)
    state_id=fields.Many2one("res.country.state", 'State', required=True)
    country_id=fields.Many2one('res.country', 'Country', required=True)

    @api.onchange('name')
    def onchange_name(self):
        if not self.name:
            return {'value': {'code': False}}
        val = {
            'code': (self.name and len(self.name)>=4 and self.name[:4].upper() or False)
        }
        return {'value': val}
                
    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            country_id = self.env['res.country.state'].browse(self.state_id.id).country_id.id
            return {'value':{'country_id':country_id}}
        return {}

AssigneeMaster()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: