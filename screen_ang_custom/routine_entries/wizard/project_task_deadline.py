# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from odoo.exceptions import UserError

class ProjectTaskDeadLine(models.Model):
    _name = "project.task.deadline"
    _description = "Project Task Deadline Change"

    name= fields.Text('Reason')
    new_date_deadline=fields.Date('New Deadline Date')
    date_deadline=fields.Date('Current Deadline Date')
    state=fields.Selection([('new','Waiting for Approval'),('approve','Approved')],'State',default='new')
    task_id=fields.Many2one('project.task','Task')
    project_id=fields.Many2one('project.project',related='task_id.project_id',string='Project',store=True)

    # _defaults = {
    #     'state':'new',
    # }
    @api.multi
    def create_record(self):
        return True

    @api.model
    def create(self, vals):
        context=self._context
        vals['task_id'] = 'task_id' in context and context['task_id'] or False
        vals['date_deadline'] = 'date_deadline' in context and context['date_deadline'] or False
        if 'task_id' in context and context['task_id']:
            task = self.env['project.task'].browse(context['task_id'])
            searids = self.env['case.tasks.line'].search([('task_id','=',task.id)])
            start_date = False
            if len(searids):
                start_date = self.env['case.tasks.line'].browse(searids[0]).start_date
            else:
                searids = self.env['associate.tasks.line'].search([('task_id','=',task.id)])
                if len(searids):
                    start_date = self.env['case.tasks.line'].browse(searids[0]).start_date
            if start_date:
                if vals['new_date_deadline']<start_date:
                    raise UserError(_('Error'),_('New Deadline date should be Greater than/ Equal to Start date in the Case Sheet ' + str(start_date)))
                
        return super(ProjectTaskDeadLine, self).create(vals)

    @api.multi
    def update_date_deadline(self):
        for obj in self:
            self.env['project.task'].write(obj.task_id.id, {'date_deadline':obj.new_date_deadline})
            task = self.env['project.task'].browse(obj.task_id.id)
            searids = self.env['case.tasks.line'].search([('task_id','=',task.id)])
            if len(searids):
                self.env['case.tasks.line'].write(searids, {'planned_completion_date':obj.new_date_deadline})
                self.env['case.tasks.line'].update_days(searids)
            else:
                searids = self.env['associate.tasks.line'].search([('task_id','=',task.id)])
                if len(searids):
                    self.env['case.tasks.line'].write(searids, {'planned_completion_date':obj.new_date_deadline})
            self.env['project.task.deadline'].write([obj.id], {'state':'approve'})

ProjectTaskDeadLine()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: