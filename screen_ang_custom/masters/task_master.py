# -*- coding: utf-8 -*-
from odoo import fields, models, api


class TaskMaster(models.Model):
    _name = 'task.master'

    name=fields.Char('Task Title',size=128, required=True)
    task_type=fields.Selection([('standard','Standard'),('regular','New')], 'Task Type', required=True, default='standard')
    product_id=fields.Many2one('product.product','Related Product')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Task Title must be Unique!')
    ]    

    @api.model
    def create(self,vals):
        product_id = self.env['product.product'].create({'name':vals['name'],'type':'service'})
        vals['product_id'] = product_id.id
        return super(TaskMaster, self).create(vals)
    
TaskMaster()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: