# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    # branch_id= fields.Many2one('sale.shop','Branch', required=False)

ResUsers()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: