from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class AddTimesheet(models.TransientModel):
    _name = "add.timesheet"
    _description = "Add Timesheet"

    @api.one
    @api.depends('start_time', 'end_time')
    def _compute_no_of_hours(self):
        if self.start_time and self.end_time:
            start_time1 = datetime.strptime(str(self.start_time), '%Y-%m-%d %H:%M:%S')
            end_time1 = datetime.strptime(str(self.end_time), '%Y-%m-%d %H:%M:%S')
            time_difference = end_time1 - start_time1
            total_hours = float(time_difference.days) * 24 + (float(time_difference.seconds) / 3600)
            self.unit_amount = total_hours

    @api.constrains('start_time', 'end_time')
    def _check_start_end_time_validate(self):
        if self.start_time > self.end_time:
            raise ValidationError(_('End Time cannot be set before Start Time.'))

    name=fields.Char('Description')
    date = fields.Date('Date',default=datetime.today())
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    unit_amount = fields.Float(compute='_compute_no_of_hours', string='No Of Hours')
    task_id=fields.Many2one('case.tasks.line', 'Task')
    case_id=fields.Many2one('case.sheet', 'Case Id')

    @api.multi
    def action_create_timesheet(self):
        self_date = fields.Date.from_string(self.date)
        date_today = fields.Date.from_string(fields.Date.today())
        # if self_date >= date_today and self_date <= date_today + timedelta(days=1):
        if date_today <= self_date <= date_today + timedelta(days=1):
            start_date = fields.Date.from_string(self.start_time)
            end_date = fields.Date.from_string(self.end_time)
            if start_date == end_date:
                timesheet_id = self.env['account.analytic.line'].search(
                    [('date', '=', self.date), ('task_id', '=', self.task_id.name.name), ('project_id', '=', self.case_id.project_id.id)])
                if timesheet_id:
                    raise UserError(_('You have already created Timesheet!'))
                else:
                    task_id = self.env['project.task'].search(
                        [('project_id', '=', self.case_id.project_id.id), ('task_name', '=', self.task_id.name.name)], limit=1)
                    vals = {'date': self.date, 'project_id': self.case_id.project_id.id,
                            'name': self.name, 'unit_amount': self.unit_amount, 'start_time': self.start_time,
                            'end_time': self.end_time, 'task_id': task_id.id}
                    self.env['account.analytic.line'].create(vals)
                    man_hours_id = self.env['man.hours'].search([('task_id', '=', self.task_id.id),
                                                                 ('case_id', '=', self.case_id.id), ('assign_to', '=', self.task_id.assign_to.id)])
                    if man_hours_id:
                        total_hours = self.unit_amount + man_hours_id.no_of_hours
                        man_hours_id.write({'no_of_hours': total_hours})
                    else:
                        self.env['man.hours'].create({
                            'task_id': self.task_id.id,
                            'assign_to': self.task_id.assign_to.id,
                            'no_of_hours': self.unit_amount,
                            'case_id': self.case_id.id,
                        })
            else:
                raise UserError(_('You only fill up today timesheet!'))
        else:
            raise UserError(_('You are not select today or day after today!'))
