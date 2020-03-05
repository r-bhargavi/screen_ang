# -*- coding: utf-8 -*-
import time
from odoo.report import report_sxw
from datetime import datetime
from odoo import api


class ConsolidatedBillLlpAnnexture(report_sxw.rml_parse):
    def __init__(self, name):
        super(ConsolidatedBillLlpAnnexture, self).__init__(name)
        self.localcontext.update({
            'time': time, 
            'get_date':self.get_date,
            'get_stages': self.get_stages,
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
    
report_sxw.report_sxw('report.consolidated.bill.llp.annexure', 'consolidated.bill', 'custom_addons/india_law/legal_e/report/consolidated_bill_llp_annexture.rml', parser=ConsolidatedBillLlpAnnexture, header=False)
report_sxw.report_sxw('report.consolidated.bill.hdfc.annexure', 'consolidated.bill', 'custom_addons/india_law/legal_e/report/consolidated_bill_hdfc_annexture.rml', parser=ConsolidatedBillLlpAnnexture, header=False)
report_sxw.report_sxw('report.consolidated.bill.cbi.annexure', 'consolidated.bill', 'custom_addons/india_law/legal_e/report/consolidated_bill_cbi_annexture.rml', parser=ConsolidatedBillLlpAnnexture, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: