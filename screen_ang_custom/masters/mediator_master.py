# -*- coding: utf-8 -*-
from odoo import fields, models, api


class MediatorMaster(models.Model):
    _name = 'mediator.master'

    name= fields.Char('Mediator Name',size=128, required=True)
    number=fields.Char('Mediator No',size=64, required=True)

MediatorMaster()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: