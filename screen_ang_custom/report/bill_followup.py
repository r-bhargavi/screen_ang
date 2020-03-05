# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo.report import report_sxw

class PrintBillFollowup(report_sxw.rml_parse):
    def __init__(self,name):
        super(PrintBillFollowup, self).__init__(name)
        self.localcontext.update({
            'time': time, 
            'get_date':self.get_date,
            'get_lines':self.get_lines,
            'get_lines_llp': self.get_lines_llp,
        })
    
    
    
    
    def get_lines(self, lines):
        res = []
        sl_no = 0
        for line in lines:
            sl_no = sl_no+1
            data = {'sl_no':sl_no,'name':line.name,'date':line.date}
            res.append(data)
        for i in range(1,21):
            res.append({'sl_no':'','name':'','date':''})
        return res
    
    def get_lines_llp(self, lines):
        res = []
        sl_no = 0
        for line in lines:
            sl_no = sl_no+1
            data = {'sl_no':sl_no,'name':line.name,'date':line.date}
            res.append(data)
        for i in range(1,21):
            res.append({'sl_no':'','name':'','amount':''})
        return res
    
        
    def get_date(self, dt):
        dt = datetime.strptime(dt, "%Y-%m-%d")
        dt = datetime.strftime(dt, "%d-%m-%y")
        return dt
    

report_sxw.report_sxw('report.bill.followup', 'consolidated.bill', 'custom_addons/india_law/legal_e/report/bill_followup.rml', parser=PrintBillFollowup, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: