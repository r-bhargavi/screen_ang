# -*- coding: utf-8 -*-
from odoo import fields, models, api


class HrEmployeeUpdateDept(models.Model):
    _name = "hr.employee.update.dept"
    _description = "Update the Department of the Employee"


    new_dept_id= fields.Many2one('hr.department', 'New Department')
    sub_emp_id=fields.Many2one('hr.employee','Substitute Employee')
    name=fields.Selection([('transfer','Transfer Dept'), ('resign','Resigned')], 'Type')

    @api.multi
    def update_emp_dept(self):
        emp = self.env['hr.employee'].browse(self._context['active_id'])
        sub_emp = self.env['hr.employee'].browse(self._context['sub_emp_id'])
        
        if self._context['type']=='transfer' and emp.department_id and emp.department_id.id == self._context['new_dept_id']:
            return True
        #To Update the Emp with Substitute Employee in Project and Task
        if emp.user_id:
            proj_ids = self.env['project.project'].search([('state','in',('draft','open')),('user_id','=',emp.user_id.id)])
            for proj in self.env['project.project'].browse(proj_ids):
                if sub_emp.user_id:
                    try:
                        proj.write({'user_id': sub_emp.user_id.id})
                    except Exception:
                        self.env['account.analytic.account'].write([proj.analytic_account_id.id], {'user_id': sub_emp.user_id.id})
            
                    
        #To Update the Project Team with Substitute Employee
        if emp.user_id:
            proj_ids = self.env['project.project'].search([('state','in',('draft','open')), ('members','=', emp.user_id.id)])
            for proj in self.env['project.project'].browse(proj_ids):
                proj.write({'members':[(3, emp.user_id.id)]})
                if sub_emp.user_id:
                    proj.write({'members':[(4, sub_emp.user_id.id)]})
                    
            case_ids = self.env['case.sheet'].search([('members','=', emp.user_id.id), ('state','=','inprogress')])
            for case in self.env['case.sheet'].browse(case_ids):
                case.write({'members':[(3, emp.user_id.id)]})
                if sub_emp.user_id:
                    case.write({'members':[(4, sub_emp.user_id.id)]}) 
                    
        #To Update the Employee to his New Department Not Completed Projects
        if emp.user_id and self._context['type'] == 'transfer':
            case_ids = self.env['case.sheet'].search([('division_id','=',self._context['new_dept_id']), ('state','=','inprogress'), ('project_id','!=', False)])
            for case in self.env['case.sheet'].browse(case_ids):
                case.project_id.write({'members':[(4, emp.user_id.id)]})
                case.write({'members':[(4, emp.user_id.id)]})                   
        
        #To Replace the Assigned To with Substitute Employee in Assignee Tasks
        case_task_ids = self.env['case.tasks.line'].search([('task_id.state','in',('draft', 'open', 'pending')),('assign_to','=',self._context['active_id'])])
        for task in self.env['case.tasks.line'].browse(case_task_ids):
            task.write({'assign_to': self._context['sub_emp_id']})
        
        #To Replace the Assignee with Substitute Employee in Case Sheet
        case_ids = self.env['case.sheet'].search([('state','in',('new','inprogress')),('assignee_id','=',self._context['active_id'])])
        for case in self.env['case.sheet'].browse(case_ids):
            case.write({'assignee_id': self._context['sub_emp_id']})
        
        #To Update the Department of the Employee
        if self._context['type'] == 'transfer':
            self.env['hr.employee'].write([self._context['active_id']], {'department_id':self._context['new_dept_id']})
            self.env['hr.employee'].onchange_department_id([self._context['active_id']], self._context['new_dept_id'])
        elif self._context['type'] == 'resign':
            self.env['hr.employee'].write([self._context['active_id']], {'active':False})
        
        return True    
HrEmployeeUpdateDept()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: