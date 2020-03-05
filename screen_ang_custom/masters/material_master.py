# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class MaterialMaster(models.Model):
    
    _name = 'material.master'

    @api.multi
    def _check_name_length(self):
        if self._context is None:
            context = {}
        name = self.browse(self.ids[0]).name
        if len(name)<4:
                return False
        return True

    @api.onchange('name')
    def onchange_name(self):
        if not self.name:
            return {'value': {'material_code': False}}
        val = {
            'material_code': (self.name and len(self.name)>=4 and self.name[:4].upper() or False)
        }
        return {'value': val}

    name= fields.Char('Material Title',size=128, required=True)
    material_code=fields.Char('Material Id',size=28, required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Material Title must be Unique!'),
        ('code_uniq', 'unique(material_code)', 'Material Id must be Unique!'),
    ]
MaterialMaster()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: