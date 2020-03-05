# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import xlwt
import base64
from io import BytesIO
from odoo.exceptions import UserError


class ClientCaseHistory(models.Model):
    _name = "client.case.history"
    _description = "Client wise Case History Details"

    name=fields.Many2one('res.partner','Client Name')
    case_id=fields.Many2one('case.sheet', 'File Number')
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
    case_lines= fields.Many2many('case.sheet', 'client_case_history_line_ids', 'history_id', 'casesheet_id', 'Case Sheets')

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return ['Client Name with all Case History']
        for task_line in self:
            res.append((task_line.id, 'Client Name with all Case History'))
        return res

    @api.multi
    def generate_report(self):
        context=self._context
        data = self.read(self.ids)[0]
        data['client_id'] = context['client_id']
        data['case_id'] = context['case_id']
        data['state'] = context['state']
        datas = {
             'ids': [],
             'model': 'case.sheet',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'client.case.history',
            'datas': datas,
            # 'nodestroy': True,
            'name':'Client Name With All Case History'
            }

    # GENERATE EXCEL REPORT
    @api.multi
    def generate_report(self):
        if self.case_lines:
            cr = self.env.cr
            workbook = xlwt.Workbook()
            Header_Text = 'Client Name With All Case History'
            sheet = workbook.add_sheet('All Case History')
            sheet.col(0).width = 256 * 30
            sheet.col(1).width = 256 * 30
            sheet.col(2).width = 256 * 30
            sheet.col(3).width = 256 * 30
            sheet.col(4).width = 256 * 30
            sheet.col(5).width = 256 * 30
            sheet.col(6).width = 256 * 30
            sheet.write(0, 0, 'File Number')
            sheet.write(0, 1, 'Parties')
            sheet.write(0, 2, 'Court Details')
            sheet.write(0, 3, 'Case Status')
            sheet.write(0, 4, 'Date of Listing')
            sheet.write(0, 5, 'History')
            sheet.write(0, 6, 'Next Date')
            row = 1
            for case in self.case_lines:
                status = ''
                if case.state == 'new':
                    status = 'New'
                elif case.state == 'waiting':
                    status = 'Waiting for Approval'
                elif case.state == 'inprogress':
                    status = 'In Progress'
                elif case.state == 'cancel':
                    status = 'Cancelled'
                elif case.state == 'transfer':
                    status = 'Transferred'
                elif case.state == 'won':
                    status = 'Won'
                elif case.state == 'arbitrated':
                    status = 'Arbitrated'
                elif case.state == 'withdrawn':
                    status = 'With Drawn'
                elif case.state == 'lost':
                    status = 'Lost'
                elif case.state == 'inactive':
                    status = 'Inactive'
                elif case.state == 'hold':
                    status = 'Hold'
                elif case.state == 'done':
                    status = 'Closed'
                elif case.state == 'sheet_rejected':
                    status = 'Case Sheet Rejected'
                elif case.state == 'closure_rejected':
                    status = 'Closure Rejected'
                sheet.write(row, 0, case.name)
                sheet.write(row, 1, case.client_id.name + ' v/s ' + case.opposite_party)
                sheet.write(row, 2, str(case.court_id.name or '') + ', ' + str(case.court_location_id.name or '') + ', ' + str(case.court_district_id.name or ''))
                sheet.write(row, 3, status)
                for cp in case.court_proceedings:
                    sheet.write(row, 4, cp.proceed_date or '')
                    sheet.write(row, 5, cp.name or '')
                    sheet.write(row, 6, cp.next_proceed_date or '')
                    row += 1
                row += 1
        else:
            raise UserError(_("Data not Found!"))
        stream = BytesIO()
        workbook.save(stream)
        cr.execute(""" DELETE FROM output""")
        attach_id = self.env['output'].create(
            {'name': Header_Text + '.xls', 'xls_output': base64.b64encode(stream.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'url': '/opt/download?model=output&field=xls_output&id=%s&filename=Client Name With All Case History.xls' % (
                attach_id.id),
            'target': 'new',
        }

    @api.multi
    def filter_proceedings(self):
        context=self._context
        filters = []
        # self.parent_id = self.ids[0]
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
        self.env.cr.execute('delete from client_case_history_line_ids')
        return self.write(res)

ClientCaseHistory()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: