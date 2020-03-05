# -*- coding: utf-8 -*-
from odoo import fields, models, api

        
class CountryState(models.Model):
    _description="Country state"
    _inherit = 'res.country.state'

    zone_ids= fields.One2many('state.zone', 'state_id', 'Zones')
    region=fields.Selection([('north','North'),('east','East'),('west','West'),('south','South')],'Region')


CountryState()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
