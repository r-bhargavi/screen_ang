# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CostCenter(models.Model):
    _description="Cost Center"
    _name = 'legal.cost.center'

    name=fields.Char('Name', size=64, required=True)
    office_id=fields.Many2one('ho.branch', 'Office', required=True)
    dept_ids= fields.One2many('hr.department', 'cost_id', "Departments")
    
CostCenter()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: