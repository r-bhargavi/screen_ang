# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PhaseMaster(models.Model):
    _name = 'phase.master'

    name=fields.Char('phase Name',size=128, required=True)

PhaseMaster()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: