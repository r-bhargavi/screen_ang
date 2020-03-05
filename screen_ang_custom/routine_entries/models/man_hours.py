# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ManHours(models.Model):
    _name = 'man.hours'
    _description = 'Man Hours'
    _inherit = ['mail.thread']

    task_id = fields.Many2one('case.tasks.line', 'Task')
    assign_to = fields.Many2one('hr.employee', 'Assignee To')
    no_of_hours = fields.Float('No of Hours')
    case_id = fields.Many2one('case.sheet', 'File Number')

