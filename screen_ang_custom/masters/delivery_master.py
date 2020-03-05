# -*- coding: utf-8 -*-
from odoo import fields, models, api


class DeliveryMaster(models.Model):
    _name = 'delivery.master'

    @api.onchange('name')
    def onchange_name(self):
        if not self.name:
            return {'value': {'code': False}}
        val = {
            'code': (self.name and len(self.name)>=4 and self.name[:4].upper() or False)
        }
        return {'value': val}

    name=fields.Char('Delivery Type',size=128, required=True)
    code=fields.Char('Delivery Code',size=64, required=True)

    
DeliveryMaster()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: