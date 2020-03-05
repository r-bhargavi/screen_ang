# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class legale_config_settings(models.TransientModel):
    _name = 'legale.config.settings'
    _inherit = 'res.config.settings'


    module_customer_receivable_account= fields.Boolean('Create Customer Receivable Account')
    module_hr_birthdays_dashboard= fields.Boolean('Create Employee Birthday\'s Dashboard')

    @api.model
    def create(self, values):
        res_id = super(legale_config_settings, self).create(values)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        # self.write([res_id], vals)
        res_id.write(vals)
        return res_id
