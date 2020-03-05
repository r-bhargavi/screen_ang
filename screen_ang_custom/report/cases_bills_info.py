# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo.report import report_sxw
from odoo.exceptions import ValidationError
from odoo import api, _

class CasesBillsExtraInfo(report_sxw.rml_parse):
    _name = 'report.cases.bills.info'
    total_bill_amt = 0.00
    total_bal_amt = 0.00
    def __init__(self, cr, uid, name, context=None):
        super(CasesBillsExtraInfo, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_data':self.get_data,
            'get_totals':self.get_totals,
        })        

    @api.multi
    def filter_string(self):
        context=self._context
        filters = []
        if context.has_key('client_id') and context['client_id']!=False:
            filters.append(('partner_id','=',context['client_id']))
        if context.has_key('ho_branch_id') and context['ho_branch_id']!=False:
            filters.append(('ho_branch_id','=',context['ho_branch_id']))
        if context.has_key('work_type') and context['work_type']!=False:
            filters.append(('work_type','=',context['work_type']))
        if context.has_key('date_filter') and context['date_filter']!=False:
            if context['date_filter']!='between':
                filters.append(('date_invoice',context['date_filter'],context['from_date'])) 
            else:
                filters.append(('date_invoice','>',context['from_date']))     
                filters.append(('date_invoice','<',context['to_date']))
        return filters    

    @api.multi
    def get_data(self, data):
        try:
            filters = self.filter_string(data['form'])
            search_ids = self.env['case.sheet'].search(filters, order='name')
            ret_datas = []
            ret_data = {}
            for case in search_ids:
                first_parties = ''
                opp_parties = ''
                court = ''
                flg_inv = False
                ret_data = {}
                state_list = {'new':'New','inprogress':'In Progress','cancel':'Cancelled','transfer':'Transferred', 'won':'Won', 'arbitrated':'Arbitrated', 'withdrawn':'With Drawn', 'lost':'Lost', 'inactive':'Inactive', 'done':'Closed', 'hold': 'Hold'}
                work_types = {'civillitigation':'Civil Litigation','criminallitigation':'Criminal Litigation', 'non_litigation':'Non Litigation', 'arbitration':'Arbitration', 'execution':'Execution', 'mediation':'Mediation'}
                for first in case.first_parties:
                    first_parties += (first_parties!='' and ', ' + first.name or first.name)
                for opp in case.opp_parties:
                    opp_parties += (opp_parties!='' and ', ' + opp.name or opp.name)
                if case.work_type in ('civillitigation','criminallitigation', 'execution'):
                    court = (case.court_id and case.court_id.name or '') + (case.court_location_id and ', ' + case.court_location_id.name or '') + (case.court_district_id and ', ' + case.court_district_id.name or '')
                else:
                    court = work_types[case.work_type] + ', ' + case.casetype_id.name
                ret_data.update({
                    'file_no': case.name,
                    'client_name': case.client_id.name,
                    'first_party': first_parties,
                    'opp_party': opp_parties,
                    'assignee': case.assignee_id.name,
                    'case_no': case.reg_number,
                    'total_case_amount': case.bill_type == 'fixed_price' and case.fixed_price or case.total_projected_amount,
                    'court_name': court,
                    'status': state_list[case.state],
                    'legale_number': False,
                    'date_invoice': False,
                    'amount_total': False,
                    'amount_paid': False,
                    'amount_tds': False,
                    'amount_balance': False,
                    'inv_state': False,
                    })
                case_inv_search_ids = self.env['case.sheet.invoice'].search([('invoice_id','!=',False), ('case_id','=',case.id)],order='invoice_id desc')
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
                        vouchers = self.env['account.voucher'].search([('move_id','=',line.move_id.id),('type','=','receipt')])
                        for voucher in vouchers:
                            total_paid_amt += voucher.amount
                            total_tds_amt += voucher.tds_amount
                            prcnt = (voucher.tds_amount/voucher.amount)*100
                            for lline in voucher.line_cr_ids:
                                if lline.amount>0.00 and lline.move_line_id.move_id == caseinv.invoice_id.move_id:
                                    distributed_tds_amt = (prcnt*lline.amount)/100
                                    act_tds += distributed_tds_amt
                                    act_amt += lline.amount - distributed_tds_amt
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
                if not flg_inv:
                    ret_datas.append(ret_data)
            return ret_datas    
        except NameError:
                raise ValidationError(_(''),
                     _('No Data To Generate Report'))                     

    @api.multi
    def get_totals(self,filt):
        if filt == 'bill':
            return self.total_bill_amt
        if filt == 'balance':
            return self.total_bal_amt    
        return ''
            
report_sxw.report_sxw('report.cases.bills.info', 'case.sheet', 'custom_addons/india_law/legal_e/report/cases_bills_info_view.rml', parser=CasesBillsExtraInfo, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: