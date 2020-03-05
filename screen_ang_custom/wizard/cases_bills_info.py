# -*- coding: utf-8 -*-
from datetime import datetime
import time

from odoo import fields, models,api
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
import xlwt
import base64
from io import BytesIO


class CasesBillsInfo(models.TransientModel):
    _name = "cases.bills.info"
    _description = "Cases and Bills Information"
    total_bill_amt =0.00
    total_bal_amt = 0.00
    ho_branch_id = False
    work_type = False
    client_id = False
    parent_id = False

    name=fields.Many2one('res.partner','Client Name')
    ho_branch_id=fields.Many2one('ho.branch','Location')
    case_id= fields.Many2one('case.sheet', 'File Number')
    work_type=fields.Selection([
        ('civillitigation', 'Civil Litigation'),
        ('criminallitigation', 'Criminal Litigation'),
        ('non_litigation', 'Non Litigation'),
        ('arbitration', 'Arbitration'),
        ('execution', 'Execution'),
        ('mediation', 'Mediation')], 'Type of Work')
    from_date=fields.Date('From date', default=lambda *a: time.strftime('%Y-%m-%d'))
    to_date=fields.Date('To Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    date_filter=fields.Selection([
        ('=','is equal to'),
        ('!=','is not equal to'),
        ('>','greater than'),
        ('<','less than'),
        ('>=','greater than or equal to'),
        ('<=','less than or equal to'),
        ('between','between')],'Bill Date')
    state=fields.Selection([('open','Pending'),('paid','Closed')],'Bill Status')
    invoice_id=fields.Many2one('account.invoice','Bill Number')
    assignee_id= fields.Many2one('hr.employee','Assignee')
    other_assignee_id=fields.Many2one('res.partner','Other Associate')
    division_id=fields.Many2one('hr.department', 'Department/Division')
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
    case_state=fields.Selection([
        ('new','New'),
        ('inprogress','In Progress'),
        ('cancel','Cancelled'),
        ('transfer','Transferred'),
        ('done','Closed'),
        ('hold','Hold')],'Case State')
    case_bills_ids=fields.One2many('case.bills.details','case_bill_id','Rel')

    # _defaults = {
    #     'from_date':lambda *a: time.strftime('%Y-%m-%d'),
    #     'to_date':lambda *a: time.strftime('%Y-%m-%d'),
    # }
    @api.model
    def default_get(self, fields_list):
        if not self._context:
            context = {}
        self.parent_id = False
        res = super(CasesBillsInfo, self).default_get(fields_list)
        return res

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return ['Cases and Bills Info']
        for task_line in self:
            res.append((task_line.id,'Cases and Bills Info'))
        return res
    #
    @api.multi
    def clear_filters_all(self):
        res={}
        self.parent_id = False
        res['name'] = False
        res['ho_branch_id'] = False
        res['work_type'] = False
        res['from_date'] = time.strftime('%Y-%m-%d')
        res['to_date'] = time.strftime('%Y-%m-%d')
        res['date_filter'] = False
        res['next_from_date'] = time.strftime('%Y-%m-%d')
        res['next_to_date'] = time.strftime('%Y-%m-%d')
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
        self.env.cr.execute('delete from court_diary_line_ids')
        delids = self.env['case.bills.details'].search([('case_bill_id','=',self.ids[0])])
        if len(delids):
            # self.pool.get('case.bills.details').unlink(cr, uid, delids)
            delids.unlink()
        return self.write(res)
    #
    # @api.multi
    # def generate_report(self):
    #     context=self._context
    #     data = self.read(self.ids)[0]
    #     data['client_id'] = context['client_id']
    #     data['date_filter'] = context['date_filter']
    #     data['from_date'] = context['from_date']
    #     data['to_date'] = context['to_date']
    #     data['ho_branch_id'] = context['ho_branch_id']
    #     data['work_type'] = context['work_type']
    #     datas = {
    #          'ids': [],
    #          'model': 'case.sheet',
    #          'form': data
    #              }
    #     return {
    #         'type': 'ir.actions.report.xml',
    #         'report_name': 'cases.bills.info',
    #         'datas': datas,
    #         'nodestroy': True,
    #         'name':'Case and Bills Info'
    #         }

    # GENERATE EXCEL REPORT
    @api.multi
    def generate_report(self):
        if self.case_bills_ids:
            cr = self.env.cr
            workbook = xlwt.Workbook()
            Header_Text = 'Case Bills Details'
            sheet = workbook.add_sheet('Case Bills Details')
            sheet.col(0).width = 256 * 30
            sheet.col(1).width = 256 * 30
            sheet.col(2).width = 256 * 30
            sheet.col(3).width = 256 * 30
            sheet.col(4).width = 256 * 30
            sheet.col(5).width = 256 * 30
            sheet.col(6).width = 256 * 30
            sheet.col(7).width = 256 * 30
            sheet.col(8).width = 256 * 30
            sheet.col(9).width = 256 * 30
            sheet.col(10).width = 256 * 30
            sheet.col(11).width = 256 * 30
            sheet.col(12).width = 256 * 30
            sheet.col(13).width = 256 * 30
            sheet.col(14).width = 256 * 30
            sheet.col(15).width = 256 * 30
            sheet.write(0, 0, 'File Number')
            sheet.write(0, 1, 'Client Name')
            sheet.write(0, 2, 'First Party')
            sheet.write(0, 3, 'Opposite Party')
            sheet.write(0, 4, 'Assignee')
            sheet.write(0, 5, 'Register Number')
            sheet.write(0, 6, 'Total Case Amount')
            sheet.write(0, 7, 'Court Name')
            sheet.write(0, 8, 'Case Status')
            sheet.write(0, 9, 'Bill Number')
            sheet.write(0, 10, 'Bill Date')
            sheet.write(0, 11, 'Bill Amount')
            sheet.write(0, 12, 'Amount Paid')
            sheet.write(0, 13, 'Balance Amount')
            sheet.write(0, 14, 'TDS Amount')
            sheet.write(0, 15, 'Bill Status')
            row = 1
            for case in self.case_bills_ids:
                sheet.write(row, 0, case.file_no)
                sheet.write(row, 1, case.client_name)
                sheet.write(row, 2, case.first_party)
                sheet.write(row, 3, case.opp_party)
                sheet.write(row, 4, case.assignee or '')
                sheet.write(row, 5, case.case_no or '')
                sheet.write(row, 6, case.total_case_amount or '')
                sheet.write(row, 7, case.court_name or '')
                sheet.write(row, 8, case.status or '')
                sheet.write(row, 9, case.legale_number or '')
                sheet.write(row, 10, case.date_invoice or '')
                sheet.write(row, 11, case.amount_total or '')
                sheet.write(row, 12, case.amount_paid or '')
                sheet.write(row, 13, case.amount_balance or '')
                sheet.write(row, 14, case.amount_tds or '')
                sheet.write(row, 15, case.inv_state or '')
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
            'url': '/opt/download?model=output&field=xls_output&id=%s&filename=Case Bills Details.xls' % (
                attach_id.id),
            'target': 'new',
        }

    @api.onchange('location')
    def onchange_location(self):
        self.ho_branch_id = self.location
        # return True

    @api.onchange('client')
    def onchange_client(self):
        self.client_id = self.client
        # return True

    @api.onchange('work_type')
    def onchange_work_type(self):
        self.work_type = self.work_type
        # return True

    @api.multi
    def filter_string(self):
        filters = []
        context=self._context
        if 'client_id' in context and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id']))
        if 'ho_branch_id' in context and context['ho_branch_id']!=False:
            filters.append(('ho_branch_id','=',context['ho_branch_id']))
        if 'work_type' in context and context['work_type']!=False:
            filters.append(('work_type','=',context['work_type']))
        if 'case_id' in context and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        if 'assignee_id' in context and context['assignee_id']!=False:
            filters.append(('assignee_id','=',context['assignee_id']))
        if 'other_assignee_id' in context and context['other_assignee_id']!=False:
            filters.append(('other_assignee_ids.name','=',context['other_assignee_id']))
        if 'division_id' in context and context['division_id']!=False:
            filters.append(('division_id','=',context['division_id']))
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
        if 'case_state' in context and context['case_state']!=False:
            filters.append(('state','=',context['case_state']))

        return filters

    @api.multi
    def invoice_filter_string(self):
        context=self._context
        filters = [('invoice_id','!=',False)]
        if 'date_filter' in context and context['date_filter']!=False:
            if context['date_filter']!='between':
                filters.append(('invoice_id.date_invoice',context['date_filter'],context['from_date']))
            else:
                filters.append(('invoice_id.date_invoice','>',context['from_date']))
                filters.append(('invoice_id.date_invoice','<',context['to_date']))
        if 'state' in context and context['state']!=False:
            filters.append(('invoice_id.state','=',context['state']))
        if 'invoice_id' in context and context['invoice_id']!=False:
            inv = self.env['account.invoice'].browse(context['invoice_id'])
            if inv :
                filters.append(('invoice_id.legale_number','ilike',inv.legale_number))

        return filters

    @api.multi
    def get_data(self):
        try:
            delids = self.env['case.bills.details'].search([('case_bill_id','=',self.ids[0])])
            if len(delids):
                # self.pool.get('case.bills.details').unlink(cr, uid, delids)
                delids.unlink()
            filters = self.filter_string()
            inv_filters = self.invoice_filter_string()
            self.cr = self.env.cr
            self.uid = self.env.user.id
            search_ids = self.env['case.sheet'].search(filters, order='name')
            ret_datas = []
            ret_data = {}
            for case in search_ids:
                first_parties = ''
                opp_parties = ''
                court = ''
                flg_inv = False
                ret_data = {}
                state_list = {'new':'New','waiting':'Waiting for Approval','inprogress':'In Progress','cancel':'Cancelled','transfer':'Transferred', 'won':'Won', 'arbitrated':'Arbitrated', 'withdrawn':'With Drawn', 'lost':'Lost', 'inactive':'Inactive', 'done':'Closed', 'hold':'Hold', 'sheet_rejected':'Case Sheet Rejected', 'closure_rejected':'Closure Rejected'}
                work_types = {'civillitigation':'Civil Litigation','criminallitigation':'Criminal Litigation', 'non_litigation':'Non Litigation', 'arbitration':'Arbitration', 'execution':'Execution', 'mediation':'Mediation'}
                for first in case.first_parties:
                    first_parties += (first_parties!='' and ', ' + first.name or first.name)
                for opp in case.opp_parties:
                    opp_parties += (opp_parties!='' and ', ' + opp.name or opp.name)
                if case.work_type in ('civillitigation','criminallitigation', 'execution'):
                    court = (case.court_id and case.court_id.name or '') + (case.court_location_id and ', ' + case.court_location_id.name or '') + (case.court_district_id and ', ' + case.court_district_id.name or '')
                else:
                    court = work_types[case.work_type] + ', ' + case.casetype_id.name
                ret_data['file_no'] = case.name
                ret_data['client_name'] = case.client_id.name
                ret_data['first_party'] = first_parties
                ret_data['opp_party'] = opp_parties
                ret_data['assignee'] = case.assignee_id.name
                ret_data['case_no'] = case.reg_number
                ret_data['total_case_amount'] = case.bill_type == 'fixed_price' and case.fixed_price or case.total_projected_amount
                ret_data['court_name'] = court
                ret_data['status'] = state_list[case.state]
                ret_data['legale_number'] = False
                ret_data['date_invoice'] = False
                ret_data['amount_total'] = False
                ret_data['amount_paid'] = False
                ret_data['amount_tds'] = False
                ret_data['amount_balance'] = False
                ret_data['inv_state'] = False
                ret_data['case_bill_id'] = self.ids[0]
                self.parent_id = self.ids[0]
                case_inv_search_ids = self.env['case.sheet.invoice'].search([('case_id','=',case.id)] + inv_filters,order='invoice_id desc')
                for caseinv in case_inv_search_ids:
                    flg_inv = True
                    bill_no = ''
                    total_paid_amt = 0.00
                    total_tds_amt = 0.00
                    distributed_tds_amt = 0.00
                    act_tds = 0.00
                    act_amt = 0.00

                    if caseinv.invoice_id.legale_number:
                        bill_no = caseinv.invoice_id.legale_number
                    else:
                        bill_no = caseinv.invoice_id.number
                    for line in caseinv.invoice_id.payment_ids:
                        # vouchers = self.env['account.voucher'].search([('move_id','=',line.move_id.id),('type','=','receipt')])
                        vouchers = self.env['account.payment'].search([('id','=',line.id)])
                        for voucher in vouchers:
                            total_paid_amt += voucher.amount
                            # total_tds_amt += voucher.tds_amount
                            # prcnt = (voucher.tds_amount/(voucher.tds_amount + voucher.amount))*100
                            # for lline in voucher.payment_line_ids:
                                # if lline.amount>0.00 and lline.move_line_id.move_id == caseinv.invoice_id.move_id:
                                    # distributed_tds_amt = (prcnt*lline.amount)/100
                                    # act_tds += distributed_tds_amt
                                    # act_amt += lline.amount - distributed_tds_amt
                    ret_data['legale_number'] = bill_no
                    ret_data['date_invoice'] = (caseinv.invoice_id.date_invoice and datetime.strptime(caseinv.invoice_id.date_invoice, '%Y-%m-%d').strftime('%d-%b-%y') or '')
                    ret_data['amount_total'] = caseinv.invoice_id.amount_total
                    ret_data['amount_paid'] = act_amt
                    ret_data['amount_tds'] = act_tds
                    ret_data['amount_balance'] = caseinv.invoice_id.residual
                    ret_data['inv_state'] = (caseinv.invoice_id.state=='open' and 'PENDING' or (caseinv.invoice_id.state=='paid' and 'CLOSED' or ''))
                    self.total_bill_amt += caseinv.invoice_id.amount_total
                    self.total_bal_amt += caseinv.invoice_id.residual
                    ret_datas.append(ret_data)
                    self.env['case.bills.details'].create(ret_data)
                if not flg_inv:
                    ret_datas.append(ret_data)
                    self.env['case.bills.details'].create(ret_data)
            return ret_datas
        except NameError:
                raise UserError(_(''),
                     _('No Data To Generate Report'))
                     
    def get_ids(self, cr, uid):
        ret = []
        if self.parent_id:
            for line in self.browse(self.parent_id).case_bills_ids:
                ret.append(str(line.id))
        return {"ids":ret}

CasesBillsInfo()


class CasesBillsDetails(models.TransientModel):
    _name = "case.bills.details"
    _order = "file_no"

    case_bill_id=fields.Many2one('cases.bills.info','Rel')
    file_no= fields.Char('File No')
    client_name= fields.Char('Client')
    first_party= fields.Char('First party')
    opp_party= fields.Char('Opposite party')
    assignee=fields.Char('Assignee')
    case_no= fields.Char('Reg No')
    total_case_amount= fields.Float('Total Case Amount', digits_compute=dp.get_precision('Account'))
    court_name=fields.Char('Court Name')
    status= fields.Char('Case Status')
    legale_number= fields.Char('Bill Number')
    date_invoice= fields.Char('Bill Date')
    amount_total=fields.Float('Bill Amount', digits_compute=dp.get_precision('Account'))
    amount_paid= fields.Float('Paid Amount', digits_compute=dp.get_precision('Account'))
    amount_tds= fields.Float('TDS Amount', digits_compute=dp.get_precision('Account'))
    amount_balance=fields.Float('Balance Amount', digits_compute=dp.get_precision('Account'))
    inv_state=fields.Char('Invoice State', digits_compute=dp.get_precision('Account'))

    
CasesBillsDetails()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: