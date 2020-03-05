# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AddEmployee(models.TransientModel):
    _name = "legale.add.employee"
    _description = "Add Employees"

    type= fields.Selection([('add','Add'),('remove','Remove')],'Type', default='add')
    employee_ids=fields.Many2many('hr.employee', 'add_employee_dept', 'dept_id', 'employee_id', 'Employees')
    remo_employee_id=fields.Many2one('hr.employee', 'Employee')
    new_employee_id= fields.Many2one('hr.employee', ' New Employee')
    dept_id= fields.Many2one('hr.department', 'Department')

    # _defaults = {
    #     'type': 'add',
    #     }
    @api.multi
    def update_add_remove_dept(self):
        if self._context is None:
            context = {}
            
        active_ids = self._context.get('active_ids', False)
        case_pool = self.env['case.sheet']
        department_pool = self.env['hr.department']
        project_pool = self.env['project.project']
        for data_obj in self:
            case_ids = case_pool.search([('division_id', '=', active_ids[0]), ('state','not in',['done','cancel'])])
                
            if data_obj.type == 'add':
                user_ids = []
                employee_ids = []
                if data_obj.employee_ids:
                    for emp_obj in data_obj.employee_ids:
                        employee_ids.append((4, emp_obj.id))
                        user_ids.append((4, emp_obj.user_id.id))
                for case_obj in case_ids:
                    if case_obj.project_id:
                        # project_pool.write(cr, uid, [case_obj.project_id.id], {'members': user_ids}, context=context)
                        case_obj.project_id.write({'members': user_ids})
                        # case_pool.write(cr, uid, [case_obj.id], {'members': user_ids}, context=context)
                        case_obj.write({'members': user_ids})
                # department_pool.write(cr, uid, active_ids, {'employee_ids':employee_ids}, context=context)
                department_pool.browse(active_ids[0]).write({'employee_ids':employee_ids})
            else:
                user_ids = [(3, data_obj.remo_employee_id.user_id.id)]
                employee_ids = [(3, data_obj.remo_employee_id.id)]
                if data_obj.new_employee_id:
                    user_ids += [(4, data_obj.new_employee_id.user_id.id)]
                    employee_ids += [(4, data_obj.new_employee_id.id)]
                for case_obj in case_ids:
                    if case_obj.project_id:
                        # project_pool.write(cr, uid, [case_obj.project_id.id], {'members': user_ids}, context=context)
                        case_obj.project_id.write({'members': user_ids})
                        # case_pool.write(cr, uid, [case_obj.id], {'members': user_ids}, context=context)
                        case_obj.write({'members': user_ids})
                        for line_obj in case_obj.tasks_lines:
                            if not data_obj.new_employee_id and line_obj.assign_to.id == data_obj.remo_employee_id.id:
                                raise UserError(_('Error!'), _("This employee already have tasks assigned in %s matter !\n\n Please add 'New Employee' in the update wizard."% case_obj.name))
                            if data_obj.new_employee_id and line_obj.assign_to.id == data_obj.remo_employee_id.id and line_obj.task_id and line_obj.task_id.state != 'done':
                                # self.pool.get('case.tasks.line').write(cr, uid, [line_obj.id], {'assign_to': data_obj.new_employee_id.id}, context=context)
                                line_obj.write({'assign_to': data_obj.new_employee_id.id})
                # department_pool.write(cr, uid, active_ids, {'employee_ids': employee_ids}, context=context)
                department_pool.browse(active_ids[0]).write({'employee_ids': employee_ids})
                
                
            
        return True


AddEmployee()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
