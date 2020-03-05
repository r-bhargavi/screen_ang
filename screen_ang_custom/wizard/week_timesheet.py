# -*- coding: utf-8 -*-
import time
import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WeekTimesheet(models.TransientModel):
    _name = "week.timesheet"
    _description = "Week Timesheet Report"

    @api.multi
    def _get_user(self):
        emp_obj = self.env['hr.employee']
        emp_id = emp_obj.search([('user_id', '=', self.env.user.id)])
        if not emp_id:
            raise UserError(_("Warning!"), _("Please define employee for this user!"))
        return emp_id and emp_id[0] or False

    name=fields.Many2one('hr.employee','Employee', default=_get_user)
    year= fields.Integer('Year', default=lambda *a: datetime.date.today().year)
    from_date=fields.Date('From date', default=lambda *a: time.strftime('%Y-%m-%d'))
    to_date=fields.Date('To Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    date_filter=fields.Selection([
        ('=','is equal to'),
        ('!=','is not equal to'),
        ('>','greater than'),
        ('<','less than'),
        ('>=','greater than or equal to'),
        ('<=','less than or equal to'),
        ('between','between')], 'Filter', default='between')
    
    # _defaults = {
    #     'year': lambda *a: datetime.date.today().year,
    #     'from_date':lambda *a: time.strftime('%Y-%m-%d'),
    #     'to_date':lambda *a: time.strftime('%Y-%m-%d'),
    #     'date_filter':'between',
    #     'name': _get_user
    #          }
    @api.multi
    def filter_proceedings(self):
        context=self._context
        filters = []
        if ('case_id') in context and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        if ('client_id') in context and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id']))
                  
        data_ids = self.env['case.sheet'].search(filters)
        return self.write({'case_lines':[(6, 0, data_ids)]})
        return True

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return ['Week Timesheet']
        for task_line in self:
            res.append((task_line.id,'Week Timesheet'))
        return res

    @api.multi
    def generate_report(self):
        context=self._context
        data = self.read(self.ids)[0]
        data['employee_id'] = context['employee_id']
        data['date_filter'] = context['date_filter']
        data['from_date'] = context['from_date']
        data['to_date'] = context['to_date']
        datas = {
             'ids': [],
             'model': 'hr_timesheet_sheet.sheet',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'week.timesheet',
            'datas': datas,
            'nodestroy': True,
            'name':'Weekly Timesheet'
            }

    @api.multi
    def clear_filters(self):
        res={}
        res['name'] = False
        res['case_id'] = False
        return self.write(res)

    @api.multi
    def clear_filters_all(self):
        res={}
        res['name'] = False
        res['case_id'] = False
        self.env.cr.execute('delete from work_summary_lines')
        return self.write(res)
