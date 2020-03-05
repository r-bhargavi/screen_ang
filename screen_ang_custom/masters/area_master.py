# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AreaMaster(models.Model):
    _name = 'area.master'

    name = fields.Char('Area/City Name', size=128, required=True)
    city_code = fields.Char('Area/City Code', size=64, required=True)

    @api.onchange('name')
    def onchange_name(self):
        if not self.name:
            return {'value': {'city_code': False}}
        val = {
            'city_code': (self.name and len(self.name) >= 3 and self.name[:3].upper() or False)
        }
        return {'value': val}



       
AreaMaster()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: