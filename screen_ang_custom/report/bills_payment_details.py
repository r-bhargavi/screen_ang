# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo.report import report_sxw
from odoo.exceptions import UserError
from odoo import api,_


class AllBillsPaymentDetails(report_sxw.rml_parse):
    _name = 'report.bills.payment.details'
    total_bill_amt = 0.00
    total_bal_amt = 0.00
    def __init__(self, name):
        super(AllBillsPaymentDetails, self).__init__(name)
        self.localcontext.update({
            'time': time,
            'get_data':self.get_data,
            'get_totals':self.get_totals,
        })
        
    @api.multi
    def filter_string(self):
        context=self._context
        filters = []
        filters.append(('type','=','out_invoice'))
        filters.append(('date_invoice','!=',False))
        if context.has_key('client_id') and context['client_id']!=False:
            filters.append(('partner_id','=',context['client_id']))
        if context.has_key('case_id') and context['case_id']!=False:
            filters.append(('case_id','=',context['case_id']))
        if context.has_key('state') and context['state']!=False:
            filters.append(('state','=',context['state']))
        else:
            filters.append(('state','in',['open','paid']))
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
            ret_datas = []
            ret_data = {}
            for invoice in self.env['account.invoice'].browse(data['form']['bill_lines']):
                ret_data = {}
                first_parties = ''
                opp_parties = ''
                bill_no = ''
                total_paid_amt = 0.00
                total_tds_amt = 0.00
                distributed_tds_amt = 0.00
                act_tds = 0.00
                act_amt = 0.00
                case_inv_search_ids = self.env['case.sheet.invoice'].search([('invoice_id','=',invoice.id)])
                for caseinv in case_inv_search_ids:
                    if caseinv.case_id:
                        for first in caseinv.case_id.first_parties:
                            first_parties += (first_parties!='' and ', ' + first.name or first.name)
                        for opp in caseinv.case_id.opp_parties:
                            opp_parties += (opp_parties!='' and ', ' + opp.name or opp.name)
                if invoice.legale_number:
                    bill_no = invoice.legale_number
                else:
                    bill_no = invoice.number
                for line in invoice.payment_ids:
                    #voucher_line_ids = self.pool.get('account.voucher.line').search(self.cr, self.uid, [('move_line_id','=',line.id)])
                    #for vline in self.pool.get('account.voucher.line').browse(self.cr, self.uid, voucher_line_ids):
                    #    paid_amt += vline.amount
                    vouchers = self.env['account.voucher'].search([('move_id','=',line.move_id.id),('type','=','receipt')])
                    for voucher in vouchers:
                        total_paid_amt += voucher.amount
                        total_tds_amt += voucher.tds_amount
                        prcnt = (voucher.tds_amount/(voucher.tds_amount + voucher.amount))*100
                       
                        for lline in voucher.line_cr_ids:
                            if lline.amount>0.00 and lline.move_line_id.move_id == invoice.move_id:
                                distributed_tds_amt = (prcnt*lline.amount)/100
                                act_tds += distributed_tds_amt
                                act_amt += lline.amount - distributed_tds_amt
                
                ret_data['legale_number'] = bill_no
                ret_data['date_invoice'] = (invoice.date_invoice and datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%d-%b-%y') or '')
                ret_data['first_parties'] = first_parties
                ret_data['opp_parties'] = opp_parties
                ret_data['amount_total'] = invoice.amount_total
                ret_data['amount_paid'] = act_amt
                ret_data['amount_tds'] = act_tds
                ret_data['amount_balance'] = invoice.residual
                ret_data['state'] = (invoice.state=='open' and 'PENDING' or (invoice.state=='paid' and 'CLOSED' or ''))
                self.total_bill_amt += invoice.amount_total
                self.total_bal_amt += invoice.residual
                ret_datas.append(ret_data)
            return ret_datas    
        except NameError:
                raise UserError(_(''),
                     _('No Data To Generate Report'))

    @api.multi
    def get_totals(self,filt):
        if filt == 'bill':
            return self.total_bill_amt
        if filt == 'balance':
            return self.total_bal_amt    
        return ''

    @api.multi
    def get_client_name(self, data):
        if data.has_key('form') and data['form'].has_key('client_id') and data['form']['client_id']:
            return self.env['res.partner'].read(data['form']['client_id'],['name'])['name']
        return ''

    @api.multi
    def format_date(self, date, format):
        return datetime.strptime(date, '%Y-%m-%d').strftime(format)

    @api.multi
    def check_proceedings(self, case_id):
        search_ids = self.env['court.proceedings'].search([('case_id','=',case_id)])
        if len(search_ids):
            return True
        return False  

    @api.multi
    def get_data_proceedings(self, case_id):
        search_ids = self.env['court.proceedings'].search([('case_id','=',case_id)])
        return search_ids
        
    def get_prepared_by(self,data):
        return self.pool.get('res.users').read(self.cr, self.uid, self.uid, ['name'])['name']
        return ''
    
report_sxw.report_sxw('report.bills.payment.details', 'account.invoice', 'custom_addons/india_law/legal_e/report/bills_payment_details_view.rml', parser=AllBillsPaymentDetails, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: