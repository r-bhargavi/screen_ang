# -*- coding: utf-8 -*-
import time
from odoo.report import report_sxw
from odoo import api, _
from datetime import datetime


class ConsolidatedBill(report_sxw.rml_parse):
    def __init__(self, name):
        super(ConsolidatedBill, self).__init__(name)
        self.localcontext.update({
            'time': time, 
            'get_date':self.get_date,
            'get_stages':self.get_stages,
        })

    @api.multi
    def get_date(self, dt):
        dt = datetime.strptime(dt, "%Y-%m-%d")
        dt = datetime.strftime(dt, "%d-%b-%y")
        return dt

    @api.multi
    def get_stages(self, lines):
        stages = ''
        for data_obj in lines.invoice_lines_fixed:
            stages += data_obj.name + '\n'
        for data_obj in lines.invoice_lines_other_expenses:
            stages += data_obj.name + '\n'
        return stages
    
report_sxw.report_sxw('report.consolidated.bill.annexure', 'consolidated.bill', 'custom_addons/india_law/legal_e/report/consolidate_bill.rml', parser=ConsolidatedBill, header=False)
report_sxw.report_sxw('report.consolidated.annexure.bill', 'consolidated.bill', 'custom_addons/india_law/legal_e/report/consolidated_annexure_report.rml', parser=ConsolidatedBill, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: