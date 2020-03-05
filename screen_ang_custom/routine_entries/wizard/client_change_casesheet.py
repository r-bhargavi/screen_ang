# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ClientChangeCasesheet(models.Model):
    _name = "client.change.casesheet"
    _description = "Client Change for Casesheet's"


    name= fields.Many2one('res.partner','Client Name')
    change_client_id= fields.Many2one('res.partner','Client Name')
    contact_partner1_id= fields.Many2one('res.partner','Contact Person 1')
    contact_partner2_id= fields.Many2one('res.partner','Contact Person 2')

    date=fields.Date('Date')
    ho_branch_id=fields.Many2one('ho.branch','Location')
    company_ref_no=fields.Char('Client Ref #',size=40, track_visibility='onchange')
    our_client=fields.Selection([('first','First Party'),('opposite','Opposite Party')],'Side')
    client_service_executive_id= fields.Many2one('hr.employee','Client Service Admin')
    client_service_manager_id= fields.Many2one('hr.employee','Client Relationship Manager')
    state_id=fields.Many2one('res.country.state', string='State')
    district_id=fields.Many2one('district.district', 'Assignee District')
    group_val=fields.Selection([('individual','INDIVIDUAL'),('proprietary','PROPRIETARY'),('company','COMPANY'),('firm','FIRM'),('llp','LLP'),('trust','TRUST'),('bank','BANK'),('others','OTHERS')],'Group')
    division_id=fields.Many2one('hr.department', 'Department/Division')
    work_type=fields.Selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work')
    casetype_id= fields.Many2one('case.master','Case Type')
    court_district_id= fields.Many2one('district.district','Court District')
    court_location_id= fields.Many2one('court.location','Court Location')
    court_id= fields.Many2one('court.master','Court Name')
    arbitrator_id= fields.Many2one('arbitrator.master','Arbitrator')
    mediator_id= fields.Many2one('mediator.master','Mediator')
    lodging_number=fields.Char('Lodging Number')
    lodging_date=fields.Date('Lodging Date')
    reg_number=fields.Char('Case No.')
    reg_date=fields.Date('Case Date')
    lot_name= fields.Char('Lot Number')
    change_case_sheet_ids=fields.Many2many('case.sheet','case_change_new_client_rel', 'change_id','case_id','File Numbers to change Client')
    change_case_sheet_office_ids=fields.Many2many('case.sheet','case_change_new_client_office_rel', 'change_office_id','case_id','File Numbers to change Client')
    flg_change=fields.Boolean('Button Change Clicked?', default=False)
    office_id= fields.Many2one('ho.branch','Office')
    filter= fields.Selection([('client', 'Client'), ('office', 'Office')], 'Filter Based On', default='client')
    #
    # _defaults = {
    #     'flg_change':False,
    #     'filter': 'client',
    # }
    @api.multi
    def update_project_details(self, case, from_id, to_id):
        # task_pool = self.env['project.task']
        members = [(4, to_id.user_id.id)]
        # tasks_ids = task_pool.search([('project_id','=',case.project_id.id), ('state','!=','done')])
        tasks_ids = self.env['project.task'].search([('project_id','=',case.project_id.id), ('state','!=','done')])
        if from_id:
            members.append((3, from_id.user_id.id))
            # for task_obj in task_pool.browse(tasks_ids):
            for task_obj in tasks_ids:
                if task_obj.user_id.id == from_id.user_id.id:
                    # task_pool.write([task_obj.id], {'user_id': to_id.user_id.id})
                    task_obj.write({'user_id': to_id.user_id.id})

            for line_obj in case.tasks_lines:
                if line_obj.assign_to.id == from_id.id:
                    # self.env['case.tasks.line'].write([line_obj.id], {'assign_to': to_id.id})
                    line_obj.write({'assign_to': to_id.id})

        if from_id == to_id:
            project_mem = [mem.id for mem in case.project_id.members]
            case_mem = [mem.id for mem in case.members]
            if to_id not in project_mem and to_id not in case_mem: 
                if (3, from_id.user_id.id) in  members:
                    members.remove((3, from_id.user_id.id))
                    
        # self.env['project.project'].write([case.project_id.id], {'members': members})
        case.project_id.write({'members': members})
        # self.env['case.sheet'].write([case.id], {'members': members})
        case.write({'members': members})
        return True
    
    @api.multi
    def change_casesheet_client(self):
        
        for line in self:
            line.write({'flg_change':True})
            # For Each Case selected in the List
            change_case_sheet_ids = False
            if line.filter == 'client':
                change_case_sheet_ids = line.change_case_sheet_ids
            else:
                change_case_sheet_ids = line.change_case_sheet_office_ids
                
            for case in change_case_sheet_ids:
                #Change the Client for Not Completed Client tasks
                # COMMENT THIS CODE BECAUSE DONT UPDATE CLIENT ON TO DO LIST
                # for task in case.client_tasks_lines:
                #     if task.state in ('New','In Progress','Pending'): # and task.assign_to_in_client == line.name
                #         task.write({'assign_to_in_client':line.change_client_id.id})
                #Change the Client and Contact in Case Sheets
                vals = {}
                if line.change_client_id:
                    if case.client_id == line.name:
                        vals.update({'client_id': line.change_client_id.id})

                        case.project_id.write({'partner_id': line.change_client_id.id})
                        # self.env['project.project'].write([case.project_id.id], {'partner_id': line.change_client_id.id})
                        tasks_ids = self.env['project.task'].search([('project_id','=',case.project_id.id), ('state','!=','done')])
                        tasks_ids.write({'partner_id': line.change_client_id.id})
                        # self.env['project.task'].write(tasks_ids, {'partner_id': line.change_client_id.id})

                if line.contact_partner1_id:
                    vals.update({'contact_partner1_id': line.contact_partner1_id.id})
                    
                if line.contact_partner2_id:
                    vals.update({'contact_partner2_id': line.contact_partner2_id.id})
                    
                if line.date:
                    vals.update({'date': line.date})
                    
                if line.ho_branch_id:
                    vals.update({'ho_branch_id': line.ho_branch_id.id})
                    
                if line.company_ref_no:
                    vals.update({'company_ref_no': line.company_ref_no})
                    
                if line.our_client:
                    vals.update({'our_client': line.our_client})
                    
                if line.client_service_executive_id:
                    vals.update({'client_service_executive_id': line.client_service_executive_id.id})
                    self.update_project_details(case, case.client_service_executive_id, line.client_service_executive_id)
                    
                if line.client_service_manager_id:
                    vals.update({'client_service_manager_id': line.client_service_manager_id.id})
                    self.update_project_details(case, case.client_service_manager_id, line.client_service_manager_id)
                        
                if line.state_id:
                    vals.update({'state_id': line.state_id.id})
                    
                if line.district_id:
                    vals.update({'district_id': line.district_id.id})
                    
                if line.group_val:
                    vals.update({'group_val': line.group_val})
                    
                if line.division_id:
                    vals.update({'division_id': line.division_id.id})
                    
                if line.work_type:
                    vals.update({'work_type': line.work_type})
                    
                if line.casetype_id:
                    vals.update({'casetype_id': line.casetype_id.id})
                    
                if line.court_district_id:
                    vals.update({'court_district_id': line.court_district_id.id})
                    
                if line.court_location_id:
                    vals.update({'court_location_id': line.court_location_id.id})
                    
                if line.court_id:
                    vals.update({'court_id': line.court_id.id})   
                    
                if line.arbitrator_id:
                    vals.update({'arbitrator_id': line.arbitrator_id.id})
                    
                if line.mediator_id:
                    vals.update({'mediator_id': line.mediator_id.id})    
                    
                if line.lodging_number:
                    vals.update({'lodging_number': line.lodging_number}) 
                      
                if line.lodging_date:
                    vals.update({'lodging_date': line.lodging_date})   
                     
                if line.reg_number:
                    vals.update({'reg_number': line.reg_number})  
                      
                if line.reg_date:
                    vals.update({'reg_date': line.reg_date}) 
                       
                if line.lot_name:
                    vals.update({'lot_name': line.lot_name})   
                         
                case.write(vals)
        return True
