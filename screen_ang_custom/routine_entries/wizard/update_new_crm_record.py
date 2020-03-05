# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class UpdateNewCRM(models.TransientModel):

    _name = "update.new.crm"
    _description = "Update New CRM In Client"
    
    old_crm_manager_id=fields.Many2one('hr.employee', 'Old Client Relationship Manager')
    new_crm_manager_id=fields.Many2one('hr.employee', 'New Client Relationship Manager')
    
    @api.multi
    def update_add_remove_crm(self):
        partner_ids=self.env['res.partner'].search([('client_manager_id','=',self.old_crm_manager_id.id)])
        if partner_ids:
            for partner_id in partner_ids:
                partner_id.write({'client_manager_id':self.new_crm_manager_id.id})