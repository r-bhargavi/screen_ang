# -*- coding: utf-8 -*-
from odoo import fields, models,api
from odoo.tools.translate import _

class PurchaseRequisitionLine(models.Model):
    
    _inherit = 'purchase.requisition.line' 
        

    select= fields.Boolean('Select', default=False)

    # _defaults = {
    #        'select': False,
    #     }
    @api.model
    def create(self, vals):
        if vals.get('select', False):
            vals['select'] = False
        res = super(PurchaseRequisitionLine, self).create(vals)
        return res
    
PurchaseRequisitionLine()

class PurchaseRequisition(models.Model):
    
    _inherit = 'purchase.requisition' 
    
    # _defaults = {
    #        'name': '/',
    #     }
    @api.model
    def create(self, vals):
        #if vals.get('name',False)=='/':
        vals['name'] = self.env['ir.sequence'].get('purchase.order.requisition')
        res = super(PurchaseRequisition, self).create(vals)
        return res
    
PurchaseRequisition()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: