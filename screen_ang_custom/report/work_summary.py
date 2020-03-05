# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from openerp.report import report_sxw
from openerp.osv import orm

class work_summary_report(report_sxw.rml_parse):
    _name = 'report.work.summary'
    
    def __init__(self, cr, uid, name, context=None):
        super(work_summary_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'datetime':datetime,
            'get_data':self.get_data,
        })
        
    def filter_string(self, context):
        filters = []
        if 'client_id' in context and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id']))
        if 'case_id' in context and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        return filters
        
        
    def get_data(self, data):
        try:
            filters = self.filter_string(data['form'])
            search_ids = self.pool.get('case.sheet').search(self.cr, self.uid, filters, order='name')
            ret_datas = []
            ret_data = {}
            if len(search_ids):
                for case in self.pool.get('case.sheet').browse(self.cr, self.uid, search_ids):
                    first_parties = ''
                    opp_parties = ''
                    parties = ''
                    procount = 0
                    total_hours = 0    
                    
                    for first in case.first_parties:
                        first_parties += (first_parties!='' and ', ' + first.name or first.name)
                    parties = first_parties + '<b>v/s</b>'
                    first_parties += ' v/s ' 
                    for opp in case.opp_parties:
                        opp_parties += (opp_parties!='' and ', ' + opp.name or opp.name)
                    parties += opp_parties
                    
                    if case.project_id:
                        tasks_ids = self.pool.get('project.task').search(self.cr, self.uid, [('project_id','=',case.project_id.id)])
                        for task in self.pool.get('project.task').browse(self.cr, self.uid, tasks_ids):
                            total_hours += task.effective_hours
                    
                        
                    pro_search_ids = self.pool.get('court.proceedings').search(self.cr, self.uid, [('case_id','=',case.id)])
                    for proceed in case.court_proceedings:
                        ret_data = {}
                        if procount ==0:
                            ret_data['name'] = case.name
                            ret_data['first_parties'] = first_parties
                            ret_data['opp_parties'] = opp_parties
                            ret_data['client'] = case.client_id.name
                            ret_data['total_hours'] = total_hours
                        else:                            
                            ret_data['name'] = ''
                            ret_data['first_parties'] = ''
                            ret_data['opp_parties'] = ''
                            ret_data['client'] = ''
                            ret_data['total_hours'] = ''
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
                        ret_data['client'] = case.client_id.name
                        ret_data['total_hours'] = total_hours
                        ret_data['proceed_date'] = ''
                        ret_data['proceed_name'] = ''
                        ret_data['next_proceed_date'] = ''
                        ret_data['last_line'] = True
                        ret_datas.append(ret_data)    
                        
                return ret_datas
        except NameError:
                raise orm.except_orm(_(''),
                     _('No Data To Generate Report'))
                     
    def format_date(self, hours):
        return datetime.strptime(str(hours), '%H').strftime('%H:%S')
        
    
report_sxw.report_sxw('report.work.summary', 'case.sheet', 'addons/legal_e/report/work_summary_view.rml', parser=work_summary_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
