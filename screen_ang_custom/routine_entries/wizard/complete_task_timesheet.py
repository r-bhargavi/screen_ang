from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class CompleteTaskTimesheet(models.TransientModel):
    _name = "complete.task.timesheet"
    _description = "Complete Task Timesheet"

    @api.one
    @api.depends('start_time', 'end_time')
    def _compute_no_of_hours(self):
        if self.start_time and self.end_time:
            start_time1 = datetime.strptime(str(self.start_time), '%Y-%m-%d %H:%M:%S')
            end_time1 = datetime.strptime(str(self.end_time), '%Y-%m-%d %H:%M:%S')
            time_difference = end_time1 - start_time1
            total_hours = float(time_difference.days) * 24 + (float(time_difference.seconds) / 3600)
            self.no_of_hours = total_hours

    @api.constrains('start_time', 'end_time')
    def _check_start_end_time_validate(self):
        if self.start_time > self.end_time:
            raise ValidationError(_('End Time cannot be set before Start Time.'))

    name=fields.Char('Description')
    date = fields.Date('Date',default=datetime.today())
    to_do_id=fields.Many2one('client.tasks.line', 'Task')
    case_id=fields.Many2one('case.sheet', 'Case Id')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    no_of_hours = fields.Float(compute='_compute_no_of_hours', string='No Of Hours')

    @api.multi
    def action_create_task_timesheet(self):
        if self.to_do_id:
            start_date = fields.Date.from_string(self.start_time)
            end_date = fields.Date.from_string(self.end_time)
            if start_date == end_date:
                self.env['account.analytic.line'].create({
                    'date': self.date,
                    'project_id': self.case_id.project_id.id,
                    'name': self.to_do_id.name,
                    'start_time': self.start_time,
                    'end_time': self.end_time,
                    'unit_amount': self.no_of_hours,
                })
            else:
                raise UserError(_('You only fill up today timesheet!'))

