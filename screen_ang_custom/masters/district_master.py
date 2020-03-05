# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class DistrictDistrict(models.Model):
    _description="District Under a State"
    _name = 'district.district'

    state_id=fields.Many2one('res.country.state', 'State', required=True)
    name= fields.Char('District Name', size=64, required=True)
    code= fields.Char('District Code', size=4)

    # @api.model
    # def create(self, vals):
    #     if vals.get('state_id', False):
    #         if vals.get('state_id') != self._context.get('state_id'):
    #             raise UserError(_('Warning!'), _("State mismatch!"))
    #     res = super(DistrictDistrict, self).create(vals)
    #     return res
    
DistrictDistrict()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
