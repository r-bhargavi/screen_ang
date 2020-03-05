# -*- coding: utf-8 -*-
from odoo import fields, models, api

        
class StateZone(models.Model):
    _description="State Zone"
    _name = 'state.zone'

    state_id= fields.Many2one('res.country.state', 'State', required=True)
    name=fields.Char('Zone Name', size=64, required=True)
    # branch_ids= fields.One2many('sale.shop', 'zone_id', 'Branches')


StateZone()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: