# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AssociatePaymentReminder(models.TransientModel):

    _name = "associate.payment.reminder"
    _description = "Associate Payment Reminder"


    name= fields.Char('Name')

AssociatePaymentReminder()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: