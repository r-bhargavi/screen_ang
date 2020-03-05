# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo.report import report_sxw
from odoo.exceptions import ValidationError
from odoo import api,_

class ClientCaseHistoryAll(report_sxw.rml_parse):
    _name = 'report.client.case.history'
    def __init__(self, name):
        super(ClientCaseHistoryAll, self).__init__(name)
        self.localcontext.update({
            'time': time,
            'datetime':datetime,
            'get_data':self.get_data,
            'get_current_date':self.get_current_date,
            'get_client_name':self.get_client_name,
            'format_date':self.format_date,
            'check_proceedings':self.check_proceedings,
            'get_data_proceedings':self.get_data_proceedings,
            'get_prepared_by':self.get_prepared_by,
        })        

    @api.multi
    def filter_proceedings(self, data):
        context=self._context
        filters = []
        
        context = data['form']
        if 'case_id' in context and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        if 'client_id' in context and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id'])) 
        if 'state' in context and context['state']!=False:
            filters.append(('state','=',context['state']))
        if 'ho_branch_id' in context and context['ho_branch_id']!=False:
            filters.append(('ho_branch_id','=',context['ho_branch_id']))
            
        return filters

    @api.multi
    def get_data(self, data):
        try:
            ret_datas = []
            ret_data = {}
            if 'form' in data and 'case_lines' in data['form'] and len(data['form']['case_lines']):
                for case in self.env['case.sheet'].browse(data['form']['case_lines']):
                    first_parties = ''
                    opp_parties = ''
                    parties = ''
                    court = ''
                    procount = 0    
                    state_list = {'new':'New','inprogress':'In Progress','cancel':'Cancelled','transfer':'Transferred', 'won':'Won', 'arbitrated':'Arbitrated', 'withdrawn':'With Drawn', 'lost':'Lost', 'inactive':'Inactive', 'done':'Closed', 'hold': 'Hold'}
                    work_types = {'civillitigation':'Civil Litigation','criminallitigation':'Criminal Litigation', 'non_litigation':'Non Litigation', 'arbitration':'Arbitration', 'execution':'Execution', 'mediation':'Mediation'}
                    
                    for first in case.first_parties:
                        first_parties += (first_parties!='' and ', ' + first.name or first.name)
                    parties = first_parties + '<b>v/s</b>'
                    first_parties += ' v/s ' 
                    for opp in case.opp_parties:
                        opp_parties += (opp_parties!='' and ', ' + opp.name or opp.name)
                    parties += opp_parties
                    
                    if case.work_type in ('civillitigation','criminallitigation', 'execution'):
                        court = (case.court_id and case.court_id.name or '') + (case.court_location_id and ', ' + case.court_location_id.name or '') + (case.court_district_id and ', ' + case.court_district_id.name or '')
                    else:
                        court = work_types[case.work_type] + ', ' + case.casetype_id.name
                    pro_search_ids = self.env['court.proceedings'].search([('case_id','=',case.id)])
                    for proceed in case.court_proceedings:
                        ret_data = {}
                        if procount ==0:
                            ret_data['name'] = case.name
                            ret_data['first_parties'] = first_parties
                            ret_data['opp_parties'] = opp_parties
                            ret_data['court'] = court
                            ret_data['status'] = state_list[case.state]
                        else:                            
                            ret_data['name'] = ''
                            ret_data['first_parties'] = ''
                            ret_data['opp_parties'] = ''
                            ret_data['court'] = ''
                            ret_data['status'] = ''
                        ret_data['proceed_date'] = (proceed.proceed_date and datetime.strptime(proceed.proceed_date, '%Y-%m-%d').strftime('%d/%m/%Y') or '')
                        ret_data['proceed_name'] = proceed.name
                        ret_data['next_proceed_date'] = (proceed.next_proceed_date and datetime.strptime(proceed.next_proceed_date, '%Y-%m-%d').strftime('%d/%m/%Y') or '')
                        procount += 1
                        if len(pro_search_ids) == procount:
                            ret_data['last_line'] = True
                        else:
                            ret_data['last_line'] = False
                        ret_datas.append(ret_data)

                    if procount ==0:
                        ret_data = {}
                        ret_data['name'] = case.name
                        ret_data['first_parties'] = first_parties
                        ret_data['opp_parties'] = opp_parties
                        ret_data['court'] = court
                        ret_data['status'] = state_list[case.state]
                        ret_data['proceed_date'] = ''
                        ret_data['proceed_name'] = ''
                        ret_data['next_proceed_date'] = ''
                        ret_data['last_line'] = True
                        ret_datas.append(ret_data)    
                        
                return ret_datas
        except NameError:
                raise ValidationError(_(''),
                     _('No Data To Generate Report'))

    @api.multi
    def get_current_date(self):
        return time.strftime('%d/%m/%Y')

    @api.multi
    def get_client_name(self, data):
        if 'form' in data and 'client_id' in data['form'] and data['form']['client_id']:
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

    @api.multi
    def get_prepared_by(self,data):
        return self.env['res.users'].read(['name'])['name']
        return ''
    
report_sxw.report_sxw('report.client.case.history', 'case.sheet', 'custom_addons/india_law/legal_e/report/client_case_history_view.rml', parser=ClientCaseHistoryAll, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: