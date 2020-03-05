# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SuccessMsg(models.TransientModel):
    _name = "success.msg"
    _description = "Selected Date is a Holiday!"

    name= fields.Char('Selected Day is a Holiday!',size=64)

SuccessMsg()


class SuccesMsg1(models.TransientModel):
    _name = "succes.msg1"
    _description = "To Show a Message when connection to AP was successful"

    name= fields.Text('Status', readonly=True)

SuccesMsg1()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
