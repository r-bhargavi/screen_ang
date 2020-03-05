# -*- coding: utf-8 -*-
from datetime import timedelta,datetime
from odoo import fields, models, api
from odoo import netsvc


class ResetEmpLeaves(models.TransientModel):
    _name = "reset.emp.leaves"
    _description = "To Reset the Employees Leaves"

    name= fields.Many2one('hr.holidays.status','Leave Type')
    employee_ids=fields.Many2many('hr.employee', 'reset_emp_leave_rel', 'reset_id','employee_id','Employees')

    @api.multi
    def reset_leaves(self):
        context=self.env.context.copy()
        holi_status_obj = self.env['hr.holidays.status']
        self.env.cr.execute("select employee_id,max(date_to) from hr_holidays where flg_reset_leaves=true group by employee_id")
        rest = self.env.cr.dictfetchall()
        max_dates = {}
        for r in rest:
            max_dates[r['employee_id']] = r['max']
        if 'leave_type' in context and context['leave_type']:
            for emp in self.env['hr.employee'].browse(context['employee_ids'][0][2]):
                leaves_rest = holi_status_obj.get_days(emp.id)
                # leaves_rest = holi_status_obj.get_days([context['leave_type']], emp.id, False)[context['leave_type']]['remaining_leaves']

                context['employee_id'] = emp.id    
                start_dt = '1900-01-01 00:00:01'
                end_dt = '1900-01-01 00:00:01'
                if (emp.id) in max_dates:
                    start_dt = (datetime.strptime(max_dates[emp.id], '%Y-%m-%d %H:%M:%S') + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                end_dt = (datetime.strptime(start_dt, '%Y-%m-%d %H:%M:%S') + timedelta(days=leaves_rest)).strftime('%Y-%m-%d %H:%M:%S')
                
                if leaves_rest>0:
                    leave_id = self.env['hr.holidays'].create({'name':'To Reset the Leaves', 'holiday_type':'employee', 'holiday_status_id':context['leave_type'], 'employee_id':emp.id, 'number_of_days_temp':leaves_rest, 'date_from': start_dt, 'date_to': end_dt,'flg_reset_leaves':True})
                    # wf_service = netsvc.LocalService("workflow")
                    # wf_service.trg_validate('hr.holidays', leave_id, 'confirm')
                    # wf_service.trg_validate('hr.holidays', leave_id, 'validate')
                    # wf_service.trg_validate('hr.holidays', leave_id, 'second_validate')
        else:
            leave_type_ids = self.env['hr.holidays.status'].search(['|',('active','=',True),('active','=',False)])
            for leave_type in self.env['hr.holidays.status'].browse(leave_type_ids):
                self.env.cr.execute("select employee_id,max(date_to) from hr_holidays where flg_reset_leaves=true group by employee_id")
                rest = self.env.cr.dictfetchall()
                max_dates = {}
                for r in rest:
                    max_dates[r['employee_id']] = r['max']
                for emp in self.env['hr.employee'].browse(context['employee_ids'][0][2]):
                    leaves_rest = holi_status_obj.get_days([leave_type.id], emp.id, False)[leave_type.id]['remaining_leaves']
                
                    context['employee_id'] = emp.id    
                    start_dt = '1900-01-01 00:00:01'
                    end_dt = '1900-01-01 00:00:01'
                    if (emp.id) in max_dates:
                        start_dt = (datetime.strptime(max_dates[emp.id], '%Y-%m-%d %H:%M:%S') + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                    end_dt = (datetime.strptime(start_dt, '%Y-%m-%d %H:%M:%S') + timedelta(days=leaves_rest)).strftime('%Y-%m-%d %H:%M:%S')
                
                    if leaves_rest>0:
                        leave_id = self.env['hr.holidays'].create({'name':'To Reset the Leaves', 'holiday_type':'employee', 'holiday_status_id':leave_type.id, 'employee_id':emp.id, 'number_of_days_temp':leaves_rest, 'date_from': start_dt, 'date_to': end_dt,'flg_reset_leaves':True})
                        # wf_service = netsvc.LocalService("workflow")
                        # wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                        # wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                        # wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True
ResetEmpLeaves()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: