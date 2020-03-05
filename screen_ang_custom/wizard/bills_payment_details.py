# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api, _
import xlwt
import base64
from io import BytesIO
from odoo.exceptions import UserError


class BillPaymentDetails(models.TransientModel):

    _name = "bills.payment.details"
    _description = "All Bills Payment Details"


    name=fields.Many2one('res.partner','Client Name')
    case_id= fields.Many2one('case.sheet', 'File Number')
    from_date=fields.Date('From date', default=lambda *a: time.strftime('%Y-%m-%d'))
    to_date=fields.Date('To Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    date_filter=fields.Selection([('=','is equal to'),('!=','is not equal to'),('>','greater than'),('<','less than'),('>=','greater than or equal to'),('<=','less than or equal to'),('between','between')],'Bill Date')
    state=fields.Selection([('open','Pending'),('paid','Closed')],'Bill Status')
    invoice_id=fields.Many2one('account.invoice','Bill Number')
    ho_branch_id=fields.Many2one('ho.branch','Location')
    assignee_id= fields.Many2one('hr.employee','Assignee')
    other_assignee_id=fields.Many2one('res.partner','Other Associate')
    division_id=fields.Many2one('hr.department', 'Department/Division')
    work_type=fields.Selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work')
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
    case_state=fields.Selection([('new','New'), ('inprogress','In Progress'), ('cancel','Cancelled'), ('transfer','Transferred'), ('done','Closed'), ('hold','Hold')],'Case State')
    bill_lines= fields.Many2many('account.invoice', 'bills_payment_details_lines', 'bill_id', 'invoice_id', 'Invoices')

    # _defaults = {
    #     'from_date':lambda *a: time.strftime('%Y-%m-%d'),
    #     'to_date':lambda *a: time.strftime('%Y-%m-%d'),
    # }
    @api.multi
    def filter_proceedings(self):
        context=self._context
        filters = []
        filters.append(('type','=','out_invoice'))
        filters.append(('date_invoice','!=',False))
        if 'case_id' in context and context['case_id']!=False:
            filters.append(('case_id','=',context['case_id']))
        if 'client_id' in context and context['client_id']!=False:
            filters.append(('partner_id','=',context['client_id']))
        if 'state' in context and context['state']!=False:
            filters.append(('state','=',context['state']))
        else:
            filters.append(('state','in',['open','paid']))
        if 'date_filter' in context and context['date_filter']!=False:
            if context['date_filter']!='between':
                filters.append(('date_invoice',context['date_filter'],context['from_date'])) 
            else:
                filters.append(('date_invoice','>',context['from_date']))     
                filters.append(('date_invoice','<',context['to_date']))     
        if 'invoice_id' in context and context['invoice_id']!=False:
            inv = self.env['account.invoice'].browse(context['invoice_id'])
            if inv :
                filters.append(('legale_number','ilike',inv.legale_number))  
        if 'ho_branch_id' in context and context['ho_branch_id']!=False:
            filters.append(('case_id.ho_branch_id','=',context['ho_branch_id']))
        if ('assignee_id') in context and context['assignee_id']!=False:
            filters.append(('case_id.assignee_id','=',context['assignee_id']))
        if ('other_assignee_id') in context and context['other_assignee_id']!=False:
            filters.append(('case_id.other_assignee_ids.name','=',context['other_assignee_id']))
        if ('division_id') in context and context['division_id']!=False:
            filters.append(('case_id.division_id','=',context['division_id']))
        if ('work_type') in context and context['work_type']!=False:
            filters.append(('case_id.work_type','=',context['work_type']))
        if ('casetype_id') in context and context['casetype_id']!=False:
            filters.append(('case_id.casetype_id','=',context['casetype_id']))
        if ('contact_partner1_id') in context and context['contact_partner1_id']!=False:
            filters.append(('case_id.contact_partner1_id','=',context['contact_partner1_id']))
        if ('contact_partner2_id') in context and context['contact_partner2_id']!=False:
            filters.append(('case_id.contact_partner2_id','=',context['contact_partner2_id']))
        if ('company_ref_no') in context and context['company_ref_no']!=False:
            filters.append(('case_id.company_ref_no','ilike',context['company_ref_no']))
        if ('reg_number') in context and context['reg_number']!=False:
            filters.append(('case_id.reg_number','ilike',context['reg_number']))
        if ('court_district_id') in context and context['court_district_id']!=False:
            filters.append(('case_id.court_district_id','=',context['court_district_id']))
        if ('court_location_id') in context and context['court_location_id']!=False:
            filters.append(('case_id.court_location_id','=',context['court_location_id']))
        if ('court_id') in context and context['court_id']!=False:
            filters.append(('case_id.court_id','=',context['court_id']))
        if ('parent_id_manager') in context and context['parent_id_manager']!=False:
            filters.append(('case_id.assignee_id.parent_id','=',context['parent_id_manager']))
        if ('bill_type') in context and context['bill_type']!=False:
            filters.append(('case_id.bill_type','=',context['bill_type']))
        if ('first_party_name') in context and context['first_party_name']!=False:
            filters.append(('case_id.first_parties.name','ilike',context['first_party_name']))
        if ('oppo_party_name') in context and context['oppo_party_name']!=False:
            filters.append(('case_id.opp_parties.name','ilike',context['oppo_party_name']))  
        if ('case_state') in context and context['case_state']!=False:
            filters.append(('case_id.state','=',context['case_state']))
        data_ids = self.env['account.invoice'].search(filters)
        return self.write({'bill_lines':[(6, 0, data_ids.ids)]})
        # return True

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return ['Bills Payment Details']
        for task_line in self:
            res.append((task_line.id,'Bills Payment Details'))
        return res

    # @api.multi
    # def generate_report(self):
    #     context=self._context
    #     data = self.read(self.ids)[0]
    #     data['client_id'] = context['client_id']
    #     data['date_filter'] = context['date_filter']
    #     data['from_date'] = context['from_date']
    #     data['to_date'] = context['to_date']
    #     data['state'] = context['state']
    #     data['case_id'] = context['case_id']
    #     datas = {
    #          'ids': [],
    #          'model': 'account.invoice',
    #          'form': data
    #              }
    #     return {
    #         'type': 'ir.actions.report.xml',
    #         'report_name': 'bills.payment.details',
    #         'datas': datas,
    #         'nodestroy': True,
    #         'name':'Bills Payment Details'
    #         }

    # GENERATE EXCEL REPORT
    @api.multi
    def generate_report(self):
        if self.bill_lines:
            cr = self.env.cr
            workbook = xlwt.Workbook()
            Header_Text = 'Bills Payment Details'
            sheet = workbook.add_sheet('Bills Payment Details')
            sheet.col(0).width = 256 * 30
            sheet.col(1).width = 256 * 30
            sheet.col(2).width = 256 * 30
            sheet.col(3).width = 256 * 30
            sheet.col(4).width = 256 * 30
            sheet.col(5).width = 256 * 30
            sheet.col(6).width = 256 * 30
            sheet.col(7).width = 256 * 30
            sheet.write(0, 0, 'Bill Number')
            sheet.write(0, 1, 'Bill Date')
            sheet.write(0, 2, 'Party Name')
            sheet.write(0, 3, 'Bill Amount')
            sheet.write(0, 4, 'Rec Amount')
            sheet.write(0, 5, 'TDS Amount')
            sheet.write(0, 6, 'Balance')
            sheet.write(0, 7, 'Status')
            row = 1
            total_amount, total_balance = 0.00, 0.00
            for bill in self.bill_lines:
                status = ''
                if bill.state == 'draft':
                    status = 'Draft'
                elif bill.state == 'sent_for_validate':
                    status = 'Sent for Validate'
                elif bill.state == 'validation_reject':
                    status = 'Validation Rejected'
                elif bill.state == 'open':
                    status = 'Open'
                elif bill.state == 'sent_revised_bill':
                    status = 'Sent for Revised Bill'
                elif bill.state == 'revised_bill_reject':
                    status = 'Revised Bill Rejected'
                elif bill.state == 'paid':
                    status = 'Paid'
                elif bill.state == 'cancel':
                    status = 'Cancelled'
                sheet.write(row, 0, bill.number)
                sheet.write(row, 1, bill.date_invoice)
                sheet.write(row, 2, str(bill.case_id.first_party or '') + ' V/S ' + bill.partner_id.name)
                total_amount += bill.amount_total
                sheet.write(row, 3, bill.amount_total)
                # sheet.write(row, 4, bill.amount_total_signed)
                # sheet.write(row, 5, proceed.effective or '')
                total_balance += bill.residual
                sheet.write(row, 6, bill.residual if bill.residual else 0.00)
                sheet.write(row, 7, status)
                row += 1
            sheet.write(row, 3, total_amount)
            sheet.write(row, 6, total_balance)
        else:
            raise UserError(_("Data not Found!"))
        stream = BytesIO()
        workbook.save(stream)
        cr.execute(""" DELETE FROM output""")
        attach_id = self.env['output'].create(
            {'name': Header_Text + '.xls', 'xls_output': base64.b64encode(stream.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'url': '/opt/download?model=output&field=xls_output&id=%s&filename=Bills Payment Details.xls' % (
                attach_id.id),
            'target': 'new',
        }

    @api.multi
    def clear_filters(self):
        res={}
        res['name'] = False
        res['case_id'] = False
        res['state'] = False
        res['date_filter'] = False
        res['from_date'] = time.strftime('%Y-%m-%d')
        res['to_date'] = time.strftime('%Y-%m-%d')
        res['state'] = False
        res['case_state'] = False
        res['invoice_id'] = False
        res['case_id'] = False
        res['assignee_id'] = False
        res['other_assignee_id'] = False
        res['division_id'] = False
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
        self.env.cr.execute('delete from bills_payment_details_lines')
        return self.write(res)
