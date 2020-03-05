# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class CaseMaster(models.Model):
    _name = 'case.master'

    name=fields.Char('Case Title', size=128, required=True,track_visibility='onchange')
    case_data_id=fields.Char('Case Id', size=28, required=True)
    remarks=fields.Text('Remarks',track_visibility='onchange')
    parent=fields.Selection([
        ('civillitigation', 'Civil Litigation'),
        ('criminallitigation', 'Criminal Litigation'),
        ('non_litigation', 'Non Litigation'),
        ('arbitration', 'Arbitration'),
        ('execution', 'Execution'),
        ('mediation', 'Mediation')], 'Parent Type',track_visibility='onchange')
    prefixed_price=fields.Float('Pre-Fixed Price', digits=dp.get_precision('Product Price'))
    no_court=fields.Boolean('No Court')
    active= fields.Boolean('Active',track_visibility='onchange')

    @api.multi
    def _check_name_length(self,ids):
        # if context is None:
        #     context = {}
        name = self.browse(ids[0]).name
        if len(name)<4:
                return False
        return True

    @api.onchange('name')
    def onchange_name(self):
        if not self.name:
            return {'value': {'case_data_id': False}}
        val = {
            'case_data_id': (self.name and len(self.name) >= 4 and self.name[:4].upper() or False)
        }
        return {'value': val}

    _constraints = [
        (_check_name_length, 'Error! Please enter Minimum 4 charecters of Case Title.', ['Case Title'])
        ]
    _sql_constraints = [
        ('name_uniq', 'unique(name, parent, case_data_id)', 'The Combination of Case Title,Parent Type,Case Id  must be Unique!'),
        ]
CaseMaster()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: