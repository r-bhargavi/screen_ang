# -*- coding: utf-8 -*-
from odoo import fields, models, api


class LitigationTemplateLine(models.Model):
    _name = 'litigation.template.line'
    _order = 'slno asc'

    litigation_id=fields.Many2one('litigation.nonlitigation.template', 'Litigation Reference')
    slno = fields.Integer('No')
    name = fields.Many2one('product.product', 'Product', required=True)


class LitigationNonlitigationTemplates(models.Model):
    _name = 'litigation.nonlitigation.template'
    _description = 'Litigation/Nonlitigation Templates'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Selection([
        ('litigation', 'Litigation'),
        ('non_litigation', 'Non Litigation')], 'Type of Work', required=True)
    litigation_type = fields.Selection([
        ('lumpsum', 'Lumpsum'),
        ('appearance_wise', 'Appearance-wise'),
        ('fixed', 'Fixed / Lumpsum'),
        ('per_hour', 'Per Hour')], 'Type of Litigation/Nonlitigation', required=True)
    litigation_lines = fields.One2many('litigation.template.line', 'litigation_id', 'Litigation/Nonlitigation Template Lines')
