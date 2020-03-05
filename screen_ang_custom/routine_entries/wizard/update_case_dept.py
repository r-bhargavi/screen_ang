# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class UpdateCaseDept(models.TransientModel):
    _name = "update.case.dept"
    _description = "Update Case sheet Department"

    assignee_id= fields.Many2one('hr.employee','Assignee')
    office_id=fields.Many2one('ho.branch','Office')
    dept_id= fields.Many2one('hr.department', 'Department')
    new_assignee_id=fields.Many2one('hr.employee','New Assignee')
    task_assignee_id=fields.Many2one('hr.employee','New Task Assignee')
    case_ids= fields.Many2many('case.sheet', 'case_sheet_update_dept', 'case_id', 'update_id', 'Case Sheet')
    partner_id= fields.Many2one('res.partner', 'Client')

    @api.onchange('new_assignee_id')
    def onchange_new_assignee_id(self):
        if self.new_assignee_id:
            return {'value': {'task_assignee_id': self.new_assignee_id}}
        return {'value': {'task_assignee_id':False}}

    @api.onchange('office_id')
    def onchange_office_id(self):
        return {'value': {'dept_id': False}}
    
    @api.multi
    def update_project_details(self, data, case_ids, assignee_id, task_assignee_id):
        task_pool = self.env['project.task']
        for case_obj in self.env['case.sheet'].browse(case_ids):
            if case_obj.project_id:
                try:
                    case_obj.project_id.write({'user_id': assignee_id.user_id.id, 'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]})
                    # self.env['project.project'].write([case_obj.project_id.id], {'user_id': assignee_id.user_id.id, 'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]})
                    case_obj.write({'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]})
                    # self.env['case.sheet'].write([case_obj.id], {'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]})
                except Exception:
                    case_obj.project_id.write({'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]})
                    # self.env['project.project'].write([case_obj.project_id.id], {'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]})
                    case_obj.write({'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]})
                    # self.env['case.sheet'].write([case_obj.id], {'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]})
                    case_obj.project_id.analytic_account_id.write({'user_id': assignee_id.user_id.id})
                    # self.env['account.analytic.account'].write([case_obj.project_id.analytic_account_id.id], {'user_id': assignee_id.user_id.id})
            for line_obj in case_obj.tasks_lines:
                if line_obj.assign_to.id == data.assignee_id.id and line_obj.task_id and line_obj.task_id.state != 'done':
                    line_obj.write({'assign_to': task_assignee_id.id})
        return True
    
    @api.multi
    def update_emp_dept(self):
        for data in self:
            case_ids = [case.id for case in data.case_ids]
            self.update_project_details( data, case_ids, data.new_assignee_id, data.task_assignee_id)
            for case in self.env['case.sheet'].browse(case_ids):
                case.write({'assignee_id': data.new_assignee_id.id})
            # case_pool.write(case_ids, {'assignee_id': data.new_assignee_id.id})

#             case_div_ids = case_pool.search(cr, uid, [('division_id','=',data.dept_id.id), ('state','not in',['done','cancel']), ('id', 'not in', case_ids)], context=context)
#             self.update_project_details(cr, uid, ids, data, case_div_ids, data.task_assignee_id, context=context)
            
        return True
      
UpdateCaseDept()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: