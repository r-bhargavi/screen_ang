# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class WrokSummary(models.TransientModel):
    _name = "work.summary"
    _description = "Work Summary Report"

    name=fields.Many2one('res.partner','Client Name')
    case_id=fields.Many2one('case.sheet','File Number')
    state=fields.Selection([
        ('new','New'),
        ('inprogress','In Progress'),
        ('cancel','Cancelled'),
        ('transfer','Transferred'),
        ('done','Closed'),
        ('hold','Hold')],'Case State')
    ho_branch_id=fields.Many2one('ho.branch','Location')
    assignee_id= fields.Many2one('hr.employee','Assignee')
    other_assignee_id=fields.Many2one('res.partner','Other Associate')
    division_id=fields.Many2one('hr.department', 'Department/Division')
    work_type=fields.Selection([
        ('civillitigation', 'Civil Litigation'),
        ('criminallitigation', 'Criminal Litigation'),
        ('non_litigation', 'Non Litigation'),
        ('arbitration', 'Arbitration'),
        ('execution', 'Execution'),
        ('mediation', 'Mediation')], 'Type of Work')
    casetype_id= fields.Many2one('case.master','Case Type')
    contact_partner1_id= fields.Many2one('res.partner','Contact Person 1')
    contact_partner2_id= fields.Many2one('res.partner','Contact Person 2')
    company_ref_no=fields.Char('Client Ref #',size=40)
    reg_number=fields.Char('Case No.')
    court_district_id= fields.Many2one('district.district','Court District')
    court_location_id= fields.Many2one('court.location','Court Location')
    court_id= fields.Many2one('court.master','Court Name')
    parent_id_manager=fields.Many2one('hr.employee', "Manager")
    bill_type=fields.Selection([('fixed_price','Fixed Price'),('assignment_wise','Assignment Wise')],'Billing Type')
    first_party_name=fields.Char('First Party name')
    oppo_party_name=fields.Char('Opposite Party name')
    case_lines= fields.Many2many('case.sheet', 'work_summary_lines', 'summary_id', 'case_id', 'Case Sheets')

    @api.multi
    def filter_proceedings(self):
        context=self._context
        filters = []
        # if context.has_key('case_id') and context['case_id']!=False:
        if 'case_id' in context and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        if 'client_id' in context and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id']))
        if 'state' in context and context['state']!=False:
            filters.append(('state','=',context['state']))
        if 'ho_branch_id' in context and context['ho_branch_id']!=False:
            filters.append(('ho_branch_id','=',context['ho_branch_id']))
        if 'assignee_id' in context and context['assignee_id']!=False:
            filters.append(('assignee_id','=',context['assignee_id']))
        if 'other_assignee_id' in context and context['other_assignee_id']!=False:
            filters.append(('other_assignee_ids.name','=',context['other_assignee_id']))
        if 'division_id' in context and context['division_id']!=False:
            filters.append(('division_id','=',context['division_id']))
        if 'work_type' in context and context['work_type']!=False:
            filters.append(('work_type','=',context['work_type']))
        if 'casetype_id' in context and context['casetype_id']!=False:
            filters.append(('casetype_id','=',context['casetype_id']))
        if 'contact_partner1_id' in context and context['contact_partner1_id']!=False:
            filters.append(('contact_partner1_id','=',context['contact_partner1_id']))
        if 'contact_partner2_id' in context and context['contact_partner2_id']!=False:
            filters.append(('contact_partner2_id','=',context['contact_partner2_id']))
        if 'company_ref_no' in context and context['company_ref_no']!=False:
            filters.append(('company_ref_no','ilike',context['company_ref_no']))
        if 'reg_number' in context and context['reg_number']!=False:
            filters.append(('reg_number','ilike',context['reg_number']))
        if 'court_district_id' in context and context['court_district_id']!=False:
            filters.append(('court_district_id','=',context['court_district_id']))
        if 'court_location_id' in context and context['court_location_id']!=False:
            filters.append(('court_location_id','=',context['court_location_id']))
        if 'court_id' in context and context['court_id']!=False:
            filters.append(('court_id','=',context['court_id']))
        if 'parent_id_manager' in context and context['parent_id_manager']!=False:
            filters.append(('assignee_id.parent_id','=',context['parent_id_manager']))
        if 'bill_type' in context and context['bill_type']!=False:
            filters.append(('bill_type','=',context['bill_type']))
        if 'first_party_name' in context and context['first_party_name']!=False:
            filters.append(('first_parties.name','ilike',context['first_party_name']))
        if 'oppo_party_name' in context and context['oppo_party_name']!=False:
            filters.append(('opp_parties.name','ilike',context['oppo_party_name']))
                  
        data_ids = self.env['case.sheet'].search(filters)
        return self.write({'case_lines':[(6, 0, data_ids.ids)]})
        return True

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return ['Work Summary']
        for task_line in self:
            res.append((task_line.id,'Work Summary'))
        return res
    
    @api.multi
    def generate_report(self):
        context=self._context
        data = self.read(self.ids)[0]
        data['client_id'] = context['client_id']
        data['case_id'] = context['case_id']
        datas = {
             'ids': [],
             'model': 'case.sheet',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'work.summary',
            'datas': datas,
            'nodestroy': True,
            'name':'Work Summary'
            }	

    @api.multi
    def clear_filters(self):
        res={}
        res['name'] = False
        res['case_id'] = False
        res['state'] =False
        res['ho_branch_id'] = False
        res['assignee_id'] = False
        res['other_assignee_id'] = False
        res['division_id'] = False
        res['work_type'] = False
        res['casetype_id'] = False
        res['contact_partner1_id'] = False
        res['contact_partner2_id'] = False
        res['company_ref_no'] = False
        res['reg_number'] = False
        res['court_district_id'] = False
        res['court_location_id'] = False
        res['court_id'] = False
        res['parent_id_manager'] = False
        res['bill_type'] = False
        res['first_party_name'] = False
        res['oppo_party_name'] = False
        return self.write(res)

    @api.multi
    def clear_filters_all(self):
        res={}
        self.clear_filters()
        self.env.cr.execute('delete from work_summary_lines')
        return self.write(res)

WrokSummary()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: