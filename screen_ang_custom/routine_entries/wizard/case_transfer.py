# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api


class CaseTransfer(models.TransientModel):
    _name = "case.transfer"
    _description = "Transfer Case Sheet"

    name= fields.Many2one('ho.branch','Transfer to Location')
    division_id=fields.Many2one('hr.department', 'Department/Division')

    def transfer_case_sheet(self):
        context=self._context
        if ('active_id') in context and context['active_id'] and ('transfer_location') in context and context['transfer_location']:
            case = self.env['case.sheet'].browse(context['active_id'])
            transfer_location = context['transfer_location']
            division_id = context['division_id']
            datas = {}
            datas['name']='/'
            datas['date'] = time.strftime('%Y-%m-%d')
            datas['client_id'] = case.client_id.id
            datas['company_ref_no'] = case.company_ref_no
            datas['contact_partner1_id'] = (case.contact_partner1_id and case.contact_partner1_id.id or False)
            datas['contact_partner2_id'] = (case.contact_partner2_id and case.contact_partner2_id.id or False)
            datas['group_val'] = case.group_val
            datas['work_type'] = case.work_type
            datas['court_district_id'] = (case.court_district_id and case.court_district_id.id or False)
            datas['court_location_id'] = case.court_location_id and case.court_location_id.id or False
            datas['court_id'] = case.court_id and case.court_id.id or False
            datas['arbitrator_id'] = case.arbitrator_id and case.arbitrator_id.id or False
            datas['mediator_id'] = case.mediator_id and case.mediator_id.id or False
            datas['assignee_id'] = case.assignee_id and case.assignee_id.id or False
            datas['other_assignee_id'] = case.other_assignee_id and case.other_assignee_id.id or False
            datas['connected_matter'] = case.connected_matter
            datas['casetype_id'] = case.casetype_id and case.casetype_id.id or False
            datas['our_client'] = case.our_client
            datas['lodging_number'] = case.lodging_number
            datas['lodging_date'] = case.lodging_date
            datas['reg_number'] = case.reg_number
            datas['reg_date'] = case.reg_date
            datas['bill_type'] = case.bill_type
            datas['fixed_price'] = case.fixed_price
            datas['total_projected_amount'] = case.total_projected_amount
            datas['assignment_approval_date'] = case.assignment_approval_date
            datas['effective_court_proceed_amount'] = case.effective_court_proceed_amount
            datas['non_effective_court_proceed_amount'] = case.non_effective_court_proceed_amount
            datas['project_id'] = case.project_id and case.project_id.id or False
            # datas['branch_id'] = case.branch_id and case.branch_id.id or False
            datas['state'] = 'new'
            datas['close_comments'] = case.close_comments
            datas['close_date'] = case.close_date
            datas['cancel_comments'] = case.cancel_comments
            datas['cancel_date'] = case.cancel_date
            datas['state_id'] = case.state_id and case.state_id.id or False
            datas['zone_id'] = case.zone_id and case.zone_id.id or False
            datas['district_id'] = case.district_id and case.district_id.id or False
            datas['district_id_associate'] = case.district_id_associate and case.district_id_associate.id or False
            datas['location'] = case.location
            datas['division_id'] = division_id or False
            datas['ho_branch_id'] = transfer_location
            other_assignee_ids = []
            for assign in case.other_assignee_ids:
                other_assignee_ids.append((0,0,{'name':assign.name.id}))
            datas['other_assignee_ids'] = other_assignee_ids
            
            tasks_lines = []
            for line in case.tasks_lines:
                tasks_lines.append((0,0,{'name':line.name.id, 'start_date':line.start_date, 'planned_completion_date':line.planned_completion_date, 'days':line.days,'slno':line.slno, 'assignee_id':(line.assignee_id and line.assignee_id.id or False),'phase_name':(line.phase_name and line.phase_name.id or False), 'task_id':(line.task_id and line.task_id.id or False), 'assign_to':(line.assign_to and line.assign_to.id or False), 'state':line.state,'old_id':line.id}))
            datas['tasks_lines'] = tasks_lines
            associate_tasks_lines = []
            for line in case.associate_tasks_lines:
                associate_tasks_lines.append((0,0,{'name':line.name.id, 'start_date':line.start_date, 'planned_completion_date':line.planned_completion_date, 'days':line.days,'slno':line.slno, 'associate_id':(line.associate_id and line.associate_id.id or False),'phase_name':(line.phase_name and line.phase_name.id or False), 'task_id':(line.task_id and line.task_id.id or False), 'assign_to_in_associate':(line.assign_to_in_associate and line.assign_to_in_associate.id or False), 'state':line.state,'old_id':line.id}))
            datas['associate_tasks_lines'] = associate_tasks_lines
            other_expenses_lines = []
            for line in case.other_expenses_lines:
                other_expenses_lines.append((0,0,{'name':line.name, 'date':line.date, 'amount':line.amount, 'billable':line.billable, 'invoiced':line.invoiced, 'invoice_status':line.invoice_status, 'old_id':line.id}))
            datas['other_expenses_lines'] = other_expenses_lines

            # COMMENT THIS CODE BECAUSE DONT TRANSFER TO DO LIST
            # client_tasks_lines = []
            # for line in case.client_tasks_lines:
            #     client_tasks_lines.append((0,0,{'name':line.name.id, 'start_date':line.start_date, 'planned_completion_date':line.planned_completion_date, 'days':line.days,'slno':line.slno, 'assignee_id':(line.assignee_id and line.assignee_id.id or False),'phase_name':(line.phase_name and line.phase_name.id or False), 'task_id':(line.task_id and line.task_id.id or False), 'assign_to_in_client':(line.assign_to_in_client and line.assign_to_in_client.id or False), 'state':line.state,'old_id':line.id}))
            # datas['client_tasks_lines'] = client_tasks_lines
            
            associate_payment_lines = []
            lineids = []
            for line in case.associate_payment_lines:
                associate_payment_lines.append((0,0,{'name':line.name.id, 'date':line.date, 'description':line.description, 'amount':line.amount,'invoiced':line.invoiced, 'state':line.state,'invoice_id':(line.invoice_id and line.invoice_id.id or False), 'associate_id':(line.associate_id and line.associate_id.id or False), 'old_id':line.id}))
                lineids.append(line.id)
                # lineids.write({'invoice_id':False})
                # self.pool.get('associate.payment').write(lineids,{'invoice_id':False})
            datas['associate_payment_lines'] = associate_payment_lines
            
            first_parties = []
            for line in case.first_parties:
                first_parties.append((0,0,{'name':line.name, 'type':line.type}))
            datas['first_parties'] = first_parties
            opp_parties = []
            for line in case.opp_parties:
                opp_parties.append((0,0,{'name':line.name, 'type':line.type}))
            datas['opp_parties'] = opp_parties

            lineids = []
            stage_lines = []
            for line in case.stage_lines:
                stage_lines.append((0,0,{'name':line.name.id, 'description':line.description,'office_id': line.office_id.id,'assignee_id':(line.assignee_id and line.assignee_id.id or False),'percent_amount':line.percent_amount, 'amount':line.amount, 'out_of_pocket_amount':line.out_of_pocket_amount, 'invoiced':line.invoiced, 'state':line.state,'invoice_id':(line.invoice_id and line.invoice_id.id or False), 'old_id':line.id}))
                lineids.append(line.id)
                # lineids.write({'invoice_id':False})
                # self.pool.get('fixed.price.stages').write(cr, uid, lineids,{'invoice_id':False})
            datas['stage_lines'] = stage_lines
            assignment_hourly_lines = []
            for line in case.assignment_hourly_lines:
                assign_hourly_invoice_ids = []
                for invline in line.invoice_ids:
                    assign_hourly_invoice_ids.append((0,0,{'name':(invline.name and invline.name.id or False),'hours':invline.hours}))
                assignment_hourly_lines.append((0,0,{'name':line.name.id, 'description':line.description, 'type':line.type, 'hours_spent':line.hours_spent, 'hours_planned':line.hours_planned, 'amount':line.amount, 'out_of_pocket_amount':line.out_of_pocket_amount, 'invoiced':line.invoiced, 'invoice_ids':assign_hourly_invoice_ids, 'billed_hours':line.billed_hours, 'remaining_hours':line.remaining_hours, 'old_id':line.id}))
            datas['assignment_hourly_lines'] = assignment_hourly_lines
            
            lineids = []
            assignment_fixed_lines = []
            for line in case.assignment_fixed_lines:
                assign_fixed_invoice_ids = []
                for invline in line.invoice_ids:
                    assign_fixed_invoice_ids.append((0,0,{'name':(invline.name and invline.name.id or False),'hours':invline.hours}))
                assignment_fixed_lines.append((0,0,{'name':line.name.id, 'description':line.description, 'type':line.type, 'hours_spent':line.hours_spent, 'hours_planned':line.hours_planned, 'amount':line.amount, 'out_of_pocket_amount':line.out_of_pocket_amount, 'invoiced':line.invoiced, 'invoice_ids':assign_fixed_invoice_ids, 'billed_hours':line.billed_hours, 'remaining_hours':line.remaining_hours, 'old_id':line.id}))
            datas['assignment_fixed_lines'] = assignment_fixed_lines
            
            court_proceedings = []
            for line in case.court_proceedings:
                court_proceedings.append((0,0,{'name':line.name, 'proceed_date':line.proceed_date, 'flg_next_date':line.flg_next_date, 'next_proceed_date':line.next_proceed_date, 'billable':line.billable, 'effective':line.effective, 'invoiced':line.invoiced, 'old_id':line.id}))
            datas['court_proceedings'] = court_proceedings


            newcase_id = self.env['case.sheet'].create(datas)
            # newcase = self.env['case.sheet'].browse(newcase_id)
            
            for line in newcase_id.stage_lines:
                for li in newcase_id.tasks_lines:
                    if li.old_id.id == line.name.id:
                        line.write({'name':li.id})
                        # self.env['fixed.price.stages'].write([line.id],{'name':li.id})

            for line in newcase_id.assignment_fixed_lines:
                for li in newcase_id.tasks_lines:
                    if li.old_id.id == line.name.id:
                        line.write({'name':li.id})
                        # self.env['assignment.wise'].write([line.id],{'name':li.id})

            for line in newcase_id.assignment_hourly_lines:
                for li in newcase_id.tasks_lines:
                    if li.old_id.id == line.name.id:
                        line.write({'name':li.id})
                        # self.env['assignment.wise'].write([line.id],{'name':li.id})

            for line in newcase_id.associate_payment_lines:
                for li in newcase_id.associate_tasks_lines:
                    if li.old_id.id == line.name.id:
                        line.write({'name':li.id})
                        # self.env['associate.payment'].write([line.id],{'name':li.id})


            inwids = self.env['inward.register'].search([('file_number','=',case.id)])
            for inobj in inwids:
                if inobj.attach_id and inobj.attach_id.res_model=='case.sheet':
                    inobj.attach_id.write({'res_id':newcase_id.id})
                    # self.env['ir.attachment'].write([inobj.attach_id.id], {'res_id':newcase_id.id})
            if len(inwids)>0:
                inwids.write({'file_number':newcase_id.id})
                # self.env['inward.register'].write(inwids, {'file_number':newcase_id.id})

            outwids = self.env['outward.register'].search([('file_number','=',case.id)])
            for outobj in outwids:
                if outobj.attach_id and outobj.attach_id.res_model=='case.sheet':
                    outobj.attach_id.write({'res_id':newcase_id.id})
                    # self.env['ir.attachment'].write([outobj.attach_id.id], {'res_id':newcase_id.id})
            if len(outwids)>0:
                outwids.write({'file_number':newcase_id.id})
                # self.env['outward.register'].write(outwids, {'file_number':newcase_id.id})

            caseinvids = self.env['case.sheet.invoice'].search([('case_id','=',case.id)])
            for obj in caseinvids:
                obj.write({'case_id':newcase_id.id,'name':'Invoice For '+newcase_id.name})
                # self.env['case.sheet.invoice'].write([obj.id], {'case_id':newcase_id.id,'name':'Invoice For '+newcase_id.name})
                for line in obj.invoice_lines_fixed:
                    fprice_ids = self.env['fixed.price.stages'].search([('old_id','=',line.ref_id)])
                    line.write({'ref_id':fprice_ids and fprice_ids[0] or line.ref_id})
                for line in obj.invoice_lines_assignment_hourly:
                    assign = self.env['assignment.wise'].browse(line.ref_id)
                    assign_ids =self.env['assignment.wise'].search([('old_id','=',line.ref_id)])
                    line.write({'ref_id':assign_ids and assign_ids[0] or line.ref_id})
                for line in obj.invoice_lines_assignment_fixed:
                    assfix = self.env['assignment.wise'].search([('old_id','=',line.ref_id)])
                    line.write({'ref_id':assfix and assfix[0] or line.ref_id})
                for line in obj.invoice_lines_other_expenses:
                    othexp = self.env['other.expenses'].search([('old_id','=',line.ref_id)])
                    line.write({'ref_id':othexp and othexp[0] or line.ref_id})
                for line in obj.invoice_lines_court_proceedings_fixed:
                    crtpro = self.env['court.proceedings'].search([('old_id','=',line.ref_id)])
                    line.write({'ref_id':crtpro and crtpro[0] or line.ref_id})
                for line in obj.invoice_lines_court_proceedings_assignment:
                    crtpro = self.env['court.proceedings'].search([('old_id','=',line.ref_id)])
                    line.write({'ref_id':crtpro and crtpro[0] or line.ref_id})

            if case.project_id:
                proj_id = case.project_id.write({'name':newcase_id.name})
                # proj_id = self.env['project.project'].write([case.project_id.id], {'name':newcase_id.name})
            return case.write({'state':'transfer','project_id':False, 'transfer_location_id':transfer_location, 'transfer_file_number_id':newcase_id.id})
            # return self.env['case.sheet'].write([case.id], {'state':'transfer','project_id':False, 'transfer_location_id':transfer_location, 'transfer_file_number_id':newcase_id.id})


CaseTransfer()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: