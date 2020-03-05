# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo import SUPERUSER_ID

        
class FollowupRemark(models.Model):
    _name = "legal.followup.remark"
    _order = "sl_no"

    name=fields.Char('Name', size=64, required=True)
    sl_no=fields.Integer('Sequence', required=True)

FollowupRemark()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
