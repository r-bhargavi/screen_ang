# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo import fields, models, api
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo import SUPERUSER_ID
from odoo.tools.safe_eval import safe_eval


class ConsolidatedBill(models.Model):
    _name = "consolidated.bill"
    _description = "Consolidated Bill"
    _order = "id desc"
    _inherit = ['mail.thread']
    
    @api.multi
    def get_stages(self, lines):
        stages = ''
        for data_obj in lines.invoice_lines_fixed:
            stages += data_obj.name + '\n'
        for data_obj in lines.invoice_lines_other_expenses:
            stages += data_obj.name + '\n'
        return stages
    @api.multi
    def update_status(self):
        bills = ['IFLI/1036/16','SFSPL/990/16','TCS/843/15','RLIC/806/15','TCS/799/15','RLIC/771/15','TCS/759/15','SFSPL/692/15','SFSPL/683/15','SML/682/15','SML/681/15','SML/680/15','SML/679/15','SML/678/15','RCL/673/15','SFSPL/665/15','SFSPL/664/15','PNBM/662/15','RCL/653/15','IPLI/650/15','IFLI/649/15','IFLI/648/15','FEDEX/646/15','SFSPL/644/15','PNBM/639/15','RLIC/634/15','RLIC/633/15','TCS/629/15','RLIC/627/15','BKIPL/626/15','RLIC/625/15','TCS/620/15','SFSPL/618/15','SFSPL/617/15','SFSPL/616/15','SFSPL/615/15','TCS/613/15','LTF/612/15','LTF/611/15','LTF/610/15','SFSPL/609/15','LTF/608/15','SFSPL/606/15','MCSL/602/15','TCS/599/15','SFSPL/598/15','TCFSL/596/15','TCFSL/595/15','IFLI/594/15','SFSPL/593/15','SFSPL/592/15','PNBM/591/15','PNBM/590/15','TCS/588/15','SFSPL/587/15','LTF/586/15','LTF/585/15','LTF/584/15','LTF/583/15','LTF/582/15','LTF/581/15','PNBM/578/15','SFSPL/577/15','TNIA/573/15','SML/572/15','SML/571/15','SML/570/15','TCHFL/560/15','SFSPL/558/15','IFLI/556/15','IFLI/555/15','SFSPL/554/15','TCFSL/553/15','TCFSL/552/15','SFSPL/551/15','SFSPL/550/15','SFSPL/549/15','TCS/547/15','SFSPL/546/15','SFSPL/545/15','SFSPL/544/15','SFSPL/543/15','SFSPL/526/15','SFSPL/525/15','LTF/541/15','LTF/542/15','LTF/540/15','LTF/539/15','LTF/538/15','LTF/537/15','LTF/536/15','LTF/535/15','LTF/534/15','LTF/533/15','LTF/532/15','LTF/531/15','LTF/530/15','LTF/529/15','LTF/528/15','LTF/527/15','TCS/523/15','LTF/524/15','TCFSL/520/15','TCFSL/519/15','LTF/518/15','LTF/517/15','LTF/516/15','LTF/514/15','LTF/515/15','LTF/512/15','LTF/513/15','LTF/511/15','SFSPL/521/15','SFSPL/522/15','FGIL/510/15','BSLI/508/15','BSLI/509/15','IFLI/506/15','IFLI/507/15','RLIC/505/15','SFSPL/504/15','SFSPL/503/15','TCFSL/502/15','TCFSL/489/15','TCFSL/486/15','TCFSL/484/15','TCFSL/483/15','SFSPL/480/15','SFSPL/479/15','TCS/478/15','SFSPL/477/15','SML/476/15','RLIC/475/15','SFSPL/474/15','SML/473/15','LTF/472/15','TNIA/471/15','MCSL/470/15','SML/469/15','SFSPL/466/15','RLIC/465/15','IDBI/464/15','RLIC/463/15','BSLI/462/15','RLIC/461/15','SFSPL/450/15','TCFSL/448/15','TCFSL/447/15','TCFSL/446/15','TCFSL/445/15','TCFSL/439/15','TCFSL/438/15','TCFSL/431/15','TCFSL/456/15','TCFSL/457/15','LTF/425/15','LTF/424/15','LTF/423/15','LTF/422/15','SFSPL/420/15','TCFSL/430/15','TCFSL/419/15','TCFSL/421/15','TCFSL/458/15','TCFSL/429/15','IFLI/418/15','IFLI/417/15','TCFSL/427/15','TCFSL/426/15','RLIC/453/15','TCS/414/15','SFSPL/412/15','TCS/413/15','TCFSL/410/15','TCFSL/407/15','TCFSL/406/15','TCFSL/405/15','TCFSL/404/15','TCFSL/395/15','LTF/393/15','LTF/392/15','LTF/391/15','LTF/390/15','LTF/389/15','LTF/388/15','LTF/387/15','TCS/386/15','TCS/384/15','TCFSL/383/15','SML/382/15','SML/381/15','SFSPL/379/15','TCS/378/15','TCS/377/15','SFSPL/376/15','TCFSL/374/15','TCFSL/373/15','TCFSL/372/15','SFSPL/370/15','TCFSL/369/15','TCFSL/368/15','TCFSL/367/15','TCFSL/366/15','TCFSL/365/15','TCFSL/364/15','TCFSL/363/15','TCFSL/362/15','TCFSL/361/15','TCFSL/357/15','TCFSL/356/15','TCFSL/355/15','TCFSL/354/15','TCFSL/353/15','TCFSL/352/15','LTF/351/15','LTF/350/15','LTF/349/15','LTF/348/15','LTF/347/15','LTF/346/15','LTF/345/15','TCFSL/344/15','TCFSL/343/15','TCFSL/342/15','MCSL/340/15','TCFSL/341/15','TCFSL/339/15','RLIC/337/15','RLIC/336/15','TCFSL/335/15','TCFSL/334/15','SFSPL/330/15','TCFSL/326/15','TCFSL/325/15','TCFSL/328/15','TCFSL/324/15','TCFSL/327/15','TCFSL/323/15','TCFSL/322/15','TCFSL/321/15','TCFSL/320/15','TCFSL/319/15','TCFSL/318/15','TCS/333/15','TCS/316/15','TCS/315/15','RLIC/317/15','RLIC/314/15','TCFSL/313/15','BSLI/311/15','FGIL/310/15','BSLI/312/15','RLIC/309/15','RLIC/308/15','RLIC/307/15','LTL/305/15','LTL/299/15','TCFSL/298/15','TCFSL/294/15','TCS/293/15','RLIC/292/15','TCS/291/15','TCS/290/15','TCS/289/15','TCFSL/288/15','LTF/287/15','TCFSL/286/15','TCFSL/285/15','TCFSL/284/15','TCFSL/283/15','TCFSL/282/15','TCFSL/281/15','TCFSL/280/15','TCFSL/279/15','LTF/306/15','LTF/278/15','LTF/277/15','LTF/276/15','LTF/275/15','RLIC/274/15','RLIC/273/15','TCFSL/271/15','TCFSL/270/15','SFSPL/269/15','TCFSL/267/15','TCFSL/266/15','IFLI/263/15','TCFSL/262/15','TCFSL/261/15','TCFSL/265/15','TCFSL/260/15','TCFSL/259/15','TCFSL/258/15','TCFSL/257/15','TCFSL/256/15','TCFSL/255/15','TCFSL/253/15','TCFSL/254/15','TCFSL/252/15','RLIC/249/15','IFLI/264/15','TNIA/250/15','BSLI/248/15','RLIC/247/15','TCFSL/245/15','TCFSL/246/15','TCS/243/15','SML/242/15','SFSPL/240/15','RLIC/244/15','RLIC/239/15','MCSL/241/15','TCFSL/237/15','TCFSL/236/15','TCFSL/234/15','TCFSL/233/15','TCFSL/231/15','TCFSL/230/15','TCFSL/229/15','TCFSL/228/15','LTF/226/15','RLIC/225/15','LTF/224/15','LTF/223/15','LTF/222/15','LTF/221/15','TCS/219/15','TCS/218/15','TCS/217/15','TCS/220/15','SFSPL/216/15','SFSPL/232/15','RLIC/214/15','RLIC/213/15','RLIC/212/15','RLIC/211/15','TCFSL/227/15','TCFSL/210/15','TCFSL/209/15','TCFSL/208/15','TCFSL/207/15','TCFSL/206/15','TCFSL/205/15','TCFSL/204/15','TCFSL/203/15','TCFSL/202/15','TCS/201/15','SFSPL/200/15','TCS/199/15','RLIC/198/15','TCHFL/192/15','TCFSL/178/14','TCS/157/14','TCFSL/163/14','TCFSL/167/14','TCSFL/130/14','TCFSL/123/14','TCFSL/097/14','TCFSL/100/14','TCFSL/096/14','TCFSL/095/14','TCFSL/094/14','TCFSL/093/14','TCFSL/092/14','TCFSL/091/14','LTF/072/14','LTF/071/14','LTF/070/14','LTF/069/14','LTF/082/14','TCFSL/067/14','TCFSL/066/14','TCFSL/065/14','LTF/063/14','LTF/062/14','LTF/073/14','TCFSL/057/14','TCFSL/058/14','LTF/048/14','LTF/049/14','TCFSL/044/14','TCFSL/051/14','RLIC/041/14','TCFSL/038/14','TCFSL/037/14','TCFSL/031/14','RLIC/030/14','TCFSL/029/14','TCFSL/028/14','TCFSL/027/14','TCFSL/026/14','TCFSL/025/14','TCFSL/024/14','ARLI/023/14','TCFSL/022/14','TCFSL/020/14','SML/021/14','RLIC/017/14','RLIC/016/14','RLIC/015/14','TCFSL/043/14','IFLI/013/14','TNIA/040/14','TCFSL/033/14','TNIA/036/14','TCFSL/035/14','TCFSL/004/14','RLIC/003/14','IDBI/001/14','IPLI/011/14','TCFSL/002/14','MH/IPLI012/2864/16','PI_HO/CBI15497/3016/16','PI_HO/IFLI14609/2448/16','RCL/673/15','RCL/653/15']
        bill_ids = self.search([('name', 'in', bills)])
        for bill_obj in bill_ids:
                    count = 0
                    lines = []
                    if bill_obj.case_invoice_lines:
                        count = len(bill_obj.case_invoice_lines)
                        for line in bill_obj.case_invoice_lines:
                            if line.invoice_id and line.invoice_id.state == 'paid':
                                lines.append(line)
#                    if count == len(lines):
##                             pass
##                         self.pool.get('consolidated.bill').write(cr, uid, [bill_obj.id], {'state': 'paid'})
#                    else:
#                        pass
        return True
    
    @api.onchange('work_type')
    def onchange_work_type(self):
        for record in self:
            if not record.work_type:
                record.casetype_id=False
                record.case_sheet_ids=[]

    @api.onchange('casetype_id')
    def onchange_case_type(self):
        for record in self:
            if not record.casetype_id:
                record.case_sheet_ids=[]

    @api.multi
    def update_total_amount(self):
        for rec in self:
            for inv in rec.case_invoice_lines:
                amount = 0.00
                for line in inv.invoice_lines_fixed:            
                    if line.amount:
                        amount = amount + line.amount + line.out_of_pocket_amount
                for line in inv.invoice_lines_assignment_hourly:            
                    if line.amount:
                        amount = amount + line.amount
                for line in inv.invoice_lines_assignment_fixed:            
                    if line.amount:
                        amount = amount + line.amount + line.out_of_pocket_amount
                for line in inv.invoice_lines_other_expenses:            
                    if line.amount:
                        amount = amount + line.amount
                for line in inv.invoice_lines_court_proceedings_fixed:            
                    if line.amount:
                        amount = amount + line.amount
                for line in inv.invoice_lines_court_proceedings_assignment:            
                    if line.amount:
                        amount = amount + line.amount
                inv.write({'amount_total_1':amount})
        return True

    @api.multi
    @api.depends('case_invoice_lines')
    def _get_total_amount(self):
        for rec in self:
            amount = 0.00
            for inv in rec.case_invoice_lines:                
                for line in inv.invoice_lines_fixed:            
                    if line.amount:
                        amount = amount + line.amount + line.out_of_pocket_amount
                for line in inv.invoice_lines_assignment_hourly:            
                    if line.amount:
                        amount = amount + line.amount
                for line in inv.invoice_lines_assignment_fixed:            
                    if line.amount:
                        amount = amount + line.amount + line.out_of_pocket_amount
                for line in inv.invoice_lines_other_expenses:            
                    if line.amount:
                        amount = amount + line.amount
                for line in inv.invoice_lines_court_proceedings_fixed:            
                    if line.amount:
                        amount = amount + line.amount
                for line in inv.invoice_lines_court_proceedings_assignment:            
                    if line.amount:
                        amount = amount + line.amount
            rec.amount_total = amount


    @api.multi
    def invoice_bill(self):
        for rec in self:
            line_total = 0.00
            line_parti = False
            for line in rec.invoice_lines:            
                line_total= line_total + line.amount
                line_parti = (line_parti and line_parti+', '+line.name or line.name)
            if round(line_total,2) != round(rec.amount_total,2):
                raise UserError(_('Total Amount in Billing Particulars is NOT EQUAL to Total Amount!'))
            for inv in rec.case_invoice_lines:
                inv.write({'subject':rec.subject, 'receivable_account_id':rec.receivable_account_id.id,'sale_account_id':rec.sale_account_id.id, 'expense_account_id':rec.expense_account_id.id, 'invoice_date':self._context['invoice_date'],'invoice_lines':[(0, 0, {'name':line_parti, 'amount':inv.amount_total_1, 'inv_id_bill':inv.id})]})
                inv.invoice_case_sheet()
        invoice_date = time.strftime('%Y-%m-%d')
        if ('invoice_date') in self._context and self._context['invoice_date']:
            invoice_date = self._context['invoice_date']
        else:
            raise UserError(_('Please Enter Invoice Date!'))
        self.write({'state': 'invoice','invoice_date': invoice_date})
        return True
    
    @api.multi
    @api.depends('bill_followup_ids')
    def _compute_next_followup_date(self):
        for invoice in self:
            if invoice.bill_followup_ids:
                line = len(invoice.bill_followup_ids) - 1
                invoice.next_followup_date = invoice.bill_followup_ids[line].next_date
            else:
                invoice.next_followup_date=False
    
    @api.multi
    @api.depends('case_invoice_lines','case_sheet_ids')
    def _get_client_service_manager_id(self):
        result = {}
        case_obj = False
        for invoice in self:
            if invoice.case_invoice_lines:
                case_obj = invoice.case_invoice_lines[0].case_id
            elif invoice.case_sheet_ids:
                case_obj = invoice.case_sheet_ids[0]
                
            if case_obj:
                invoice.client_service_manager_id= case_obj.client_service_manager_id.id
                invoice.branch_id= case_obj.ho_branch_id.id
                invoice.client_service_executive_id=case_obj.client_service_executive_id.id
                invoice.assignee_id=case_obj.assignee_id.id
                invoice.division_id=case_obj.division_id.id
            else:
                invoice.client_service_manager_id= False
                invoice.branch_id= False
                invoice.client_service_executive_id=False
                invoice.assignee_id=False
                invoice.division_id=False

    @api.multi
    def _get_bill(self):
        result = {}
        for line in self.env['consolidated.bill.followup'].browse():
            result[line.bill_id.id] = True
        return result.keys()

    @api.multi
    def _get_consol_bill(self):
        result = {}
        for line in self.env['case.sheet.invoice'].browse():
            result[line.consolidated_id.id] = True
        return result.keys()
    
    @api.multi
    @api.depends('case_invoice_lines')
    def _compute_bad_debts(self):
        for bill_obj in self:
            invoice_ids = [line.invoice_id for line in bill_obj.case_invoice_lines if line.invoice_id]
            invoice_ids = list(set(invoice_ids))
            bad_debts = 0.0
            for invoice in invoice_ids:
                if invoice.payment_ids:
                    for m in invoice.payment_ids:
                        if m.journal_id.id == invoice.company_id.bad_debts_journal_id.id:
                            # bad_debts += m.credit
                            bad_debts += m.amount
            bill_obj.bad_debts = bad_debts
        return bill_obj
    
    @api.multi
    @api.depends('case_invoice_lines')
    def _compute_lines(self):
        result = {}
        for bill in self:
            src = []
            lines = []
            for line in bill.case_invoice_lines:
                if line.invoice_id:
                    if line.invoice_id.move_id:
                        for m in line.invoice_id.move_id.line_ids:
                            if m.account_id != line.invoice_id.account_id:
                                continue
                            temp_lines = []
                            if m.full_reconcile_id:
                                check_ids=[]
                                for each in m.full_reconcile_id.reconciled_line_ids:
                                    if each.credit>0.0:
                                    
                                        check_ids=each
                                temp_lines = map(lambda x: x.id, check_ids)
#                            elif m.matched_credit_ids:
#                                temp_lines = map(lambda x: x.id, m.matched_credit_ids)
                            lines += [x for x in temp_lines if x not in lines]
                            src.append(m.id)

#            lines = filter(lambda x: x not in src, lines)
#            bill.write({'payment_ids': [(6, 0, lines)]})

            bill.payment_ids=[(6,0,lines)]
#            result[bill.id] = lines
#            print ("result---------",result)
#        return True
    
    @api.multi
    @api.depends('payment_ids')
    def _amount_residual(self):
        for bill in self:
            credit = 0.0
            for line in bill.payment_ids:
                credit += line.credit
            balance = bill.amount_total - credit
            bill.residual = balance

    @api.multi
    @api.depends('case_invoice_lines.case_id')
    def _compute_con_expense_prof_fee(self):
        type_name = self.env['account.account.type'].search([('name', '=', 'Expense')])
        for case in self:
            total_expense, total_proffee = 0.0, 0.0
            if case.case_invoice_lines:
                for inv in case.case_invoice_lines:
                    if inv.invoice_id.invoice_line_ids:
                        for line in inv.invoice_id.invoice_line_ids:
                            if line.account_id.user_type_id.id == type_name.id:
                                total_expense += line.price_subtotal
                            elif line.account_id.code == '2100001':
                                total_proffee += line.price_subtotal
                    case.total_expense = total_expense
                    case.total_proffee = total_proffee

    name=fields.Char('Invoice Number',size=100, track_visibility='always')
    client_id=fields.Many2one('res.partner','Client Name', required=True, track_visibility='onchange')
    work_type=fields.Selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work', required=True, track_visibility='onchange')
    casetype_id= fields.Many2one('case.master','Case Type', required=True, track_visibility='onchange')
    case_sheet_ids=fields.Many2many('case.sheet','case_consolidated_rel','bill_id','case_id','Case Sheets')
    state=fields.Selection([
        ('draft','New'),
        ('confirm','Confirmed'),
        ('invoice','Invoiced'),
        ('paid','Paid'),
        ('cancel','Cancelled')],'Status', track_visibility='onchange', default='draft')
    case_invoice_lines=fields.One2many('case.sheet.invoice','consolidated_id','Case Sheet Invoice Lines')
    amount_total=fields.Float(compute='_get_total_amount',string='Amount', track_visibility='onchange')
    invoice_lines=fields.One2many('consolidated.bill.line','inv_id_bill','Invoice Details')
    subject=fields.Text('Subject')
    invoice_date=fields.Date('Invoiced Date', track_visibility='onchange')
    receivable_account_id=fields.Many2one('account.account', 'Receivable Account', states={'confirm':[('required',True)]}, domain=[('internal_type', '=', 'receivable')], help="The partner account used for these invoices.")
    sale_account_id=fields.Many2one('account.account', 'Sales Account', states={'confirm':[('required',True)]}, help="The income or expense account related to the selected product.")
#    sale_account_id=fields.Many2one('account.account', 'Sales Account', domain=[('type','!=','view'), ('type', '!=', 'closed')], states={'confirm':[('required',True)]}, help="The income or expense account related to the selected product.")
    flg_tds_note=fields.Boolean('TDS Note')
    flg_pan_no=fields.Boolean('Company PAN Number')
    flg_fixed_fixed_price_stage=fields.Boolean('Fixed Price Stages')
    flg_fixed_other_exp_billable=fields.Boolean('Other expenses Billable')
    flg_assign_hourly_stage=fields.Boolean('Hourly Stages')
    flg_assign_fixed_price_stage=fields.Boolean('Fixed Price Stages')
    flg_assign_other_exp_billable=fields.Boolean('Other expenses Billable')
    flg_assign_court_proceed_billable=fields.Boolean('Court Proceedings Billable')
    invoice_template=fields.Selection([
        ('general','General'),
        ('india_llp','INDIALAW LLP'),
        ('hdfc', 'HDFC'),
        ('cbi', 'CBI'),
        ],'Invoice Template', default='general')

    expense_account_id= fields.Many2one('account.account', 'Expense Account', states={'confirm':[('required',True)]})
#    expense_account_id= fields.Many2one('account.account', 'Expense Account', domain=[('type','!=','view'), ('type', '!=', 'closed')], states={'confirm':[('required',True)]})
    date= fields.Date('Date')
    bill_followup_ids= fields.One2many('consolidated.bill.followup', 'bill_id', 'Bill Followup')
    # 'next_followup_date': fields.function(_compute_next_followup_date, type="date", string='Next Followup Date', store={
    #         'consolidated.bill': (lambda self, cr, uid, ids, c={}: ids, ['bill_followup_ids'], 10),
    #         'consolidated.bill.followup': (_get_bill, ['date', 'next_date'], 10),
    #     },
    #     multi='sums', help="Next Followup Date.",  track_visibility='always'),
    next_followup_date = fields.Date(compute='_compute_next_followup_date', string='Next Followup Date', store=True,help="Next Followup Date.", track_visibility='always')
    bad_debts= fields.Float(compute='_compute_bad_debts', string='Bad Debts', digits_compute=dp.get_precision('Account'),)
    # 'client_service_manager_id': fields.function(_get_client_service_manager_id, relation='hr.employee', string='Client Relationship Manager', type="Many2one", store={
    #         'consolidated.bill': (lambda self, cr, uid, ids, c={}: ids, ['case_sheet_ids','invoice_lines'], 10),
    #         'case.sheet.invoice': (_get_consol_bill, ['consolidated_id', 'case_id'], 10),
    #     },
    #     multi='sums',),
    client_service_manager_id = fields.Many2one('hr.employee', compute='_get_client_service_manager_id',string='Client Relationship Manager', store=True)
    # 'branch_id': fields.function(_get_client_service_manager_id, relation='ho.branch', string='Office', type="Many2one", store={
    #         'consolidated.bill': (lambda self, cr, uid, ids, c={}: ids, ['case_sheet_ids','invoice_lines'], 10),
    #         'case.sheet.invoice': (_get_consol_bill, ['consolidated_id', 'case_id'], 10),
    #     },
    #     multi='sums',),
    branch_id = fields.Many2one('ho.branch', compute='_get_client_service_manager_id', string='Office', store=True)
    # 'client_service_executive_id': fields.function(_get_client_service_manager_id, relation='hr.employee', string='Client Service Manager', type="Many2one", store={
    #         'consolidated.bill': (lambda self, cr, uid, ids, c={}: ids, ['case_sheet_ids','invoice_lines'], 10),
    #         'case.sheet.invoice': (_get_consol_bill, ['consolidated_id', 'case_id'], 10),
    #     },
    #     multi='sums',),
    client_service_executive_id = fields.Many2one('hr.employee', compute='_get_client_service_manager_id',string='Client Service Manager', store=True)
    # 'assignee_id': fields.function(_get_client_service_manager_id, relation='hr.employee', string='Assignee', type="Many2one", store={
    #         'consolidated.bill': (lambda self, cr, uid, ids, c={}: ids, ['case_sheet_ids','invoice_lines'], 10),
    #         'case.sheet.invoice': (_get_consol_bill, ['consolidated_id', 'case_id'], 10),
    #     },
    #     multi='sums',),
    assignee_id = fields.Many2one('hr.employee', compute='_get_client_service_manager_id', string='Assignee',store=True)
    # 'division_id': fields.function(_get_client_service_manager_id, relation='hr.department', string='Department/Division', type="Many2one", store={
    #         'consolidated.bill': (lambda self, cr, uid, ids, c={}: ids, ['case_sheet_ids','invoice_lines'], 10),
    #         'case.sheet.invoice': (_get_consol_bill, ['consolidated_id', 'case_id'], 10),
    #     },
    #     multi='sums',),
    division_id = fields.Many2one('hr.department', compute='_get_client_service_manager_id',string='Department/Division', store=True)
    due_date_over= fields.Boolean('Due Date Over', track_visibility='onchange', default=False)
    due_days_string=fields.Char('Aging', default='')
    due_date_red= fields.Boolean('Due Date Red', default=False)
    payment_ids= fields.Many2many('account.move.line',compute='_compute_lines', string='Payments')
#    payment_ids= fields.Many2many('account.move.line', string='Payments', groups='base.group_user')
    residual= fields.Float(compute='_amount_residual', digits_compute=dp.get_precision('Account'), string='Balance')
    partially_paid= fields.Boolean('Partially Paid')
    total_expense = fields.Float(compute=_compute_con_expense_prof_fee, string='Expenses Reim', digits_compute=dp.get_precision('Account'))
    total_proffee = fields.Float(compute=_compute_con_expense_prof_fee, string='Prof. Fees', digits_compute=dp.get_precision('Account'))
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address')

    # _defaults = {
    #     'state':'draft',
    #     'invoice_template':'general',
    #     'due_date_over': False,
    #     'due_date_red': False,
    #     'due_days_string': '',
    # }
    @api.multi
    def bill_due_date_scheduler(self):
        bill_ids = self.search([('state', '=', 'invoice')])
        for bill_obj in bill_ids:
            due_date = (datetime.strptime(bill_obj.invoice_date, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d')
            due_days_string = ''
            today = time.strftime('%Y-%m-%d')
            days = (datetime.strptime(today, '%Y-%m-%d') - datetime.strptime(due_date, '%Y-%m-%d')).days
            vals = {}
            if days>0:
                due_days_string = str(days) + ' days over due'
                vals.update({'due_days_string': due_days_string})
                if not bill_obj.bill_followup_ids:
                    self.env['consolidated.bill.followup'].create({
                        'name': 'Missing Followup(System Generated Messages)',
                        'date': today,
                        'next_date': today,
                        'state': 'communicate',
                        'bill_id': bill_obj.id,
                        'due_next_date_over': True,
                        })

                if days >= 30:
                    vals.update({'due_date_red': True})
            else:
                due_days_string = str(abs(days)) + ' days to over due'
                vals.update({'due_days_string': due_days_string})
            if time.strftime('%Y-%m-%d') >= due_date:
                vals.update({'due_date_over': True})
            # self.write(cr, uid, [bill_obj.id], vals, context=context)
            bill_obj.write(vals)
        bill_ids = self.search([('state', '!=', 'invoice')])
        # self.write(cr, uid, bill_ids, {'due_date_over': False, 'due_date_red': False, 'due_days_string': ''}, context=context)
        bill_ids.write({'due_date_over': False, 'due_date_red': False, 'due_days_string': ''})
        return True
    
    @api.model
    def create(self, vals):
        retvals = super(ConsolidatedBill, self).create(vals)
        return retvals

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.state !='draft':
                raise UserError(_('You cannot delete a Confirmed Consolidated Bill.'))
        return super(ConsolidatedBill, self).unlink()

    @api.multi
    def cancel_bill(self):
        case_inv_ids = self.env['case.sheet.invoice'].search([('consolidated_id','=',self.id)])
        for invoice in case_inv_ids:
            if invoice.invoice_id:
                invoice.action_cancel()
        case_inv_ids.unlink()
        self.write({'state':'cancel'})
        return True

    @api.multi
    def cancel_bill_invoice(self):
        case_inv_ids = self.env['case.sheet.invoice'].search([('consolidated_id','=',self.id)])
        for invoice in case_inv_ids:
            if invoice.invoice_id:
                invoice.invoice_id.action_cancel()
        # self.env['case.sheet.invoice'].unlink(case_inv_ids)
        case_inv_ids.unlink()
        self.write({'state':'cancel'})
        return True   

    @api.multi
    def reset_to_draft(self):
        self.write({'state':'draft'})
        return True     
    
    @api.multi
    def check_case_sheet(self, obj, lines, inv_field):
        invoice_line_obj = self.env['case.sheet.invoice.line']
        for line in lines:
            invoice_line = invoice_line_obj.search([('ref_id', '=', line.ref_id), (inv_field, '!=', obj.id), (inv_field + '.case_id', '=', obj.case_id.id),(inv_field +'.consolidated_id.state', 'not in', ('cancel', 'draft'))])
            if invoice_line:
                for inv_line in invoice_line_obj.browse(invoice_line):
                    bill = 'inv_line.' + inv_field + '.consolidated_id.name'
                    cons_name = safe_eval(bill, dict(inv_line=inv_line))
                    raise UserError(_('Warning'),_('This casesheet %s is already used in %s bill.please check.either remove the casesheet from the current bill or cancel the %s bill')%(obj.case_id.name,cons_name, cons_name))
        
        return True

    @api.multi
    def confirm_bill(self):
        obj =  self
        context = self.env.context.copy() or {}
        vals=({'consolidated_id':obj.id,
        'flg_fixed_fixed_price_stage':obj.flg_fixed_fixed_price_stage,
        'flg_fixed_other_exp_billable':obj.flg_fixed_other_exp_billable,
        'flg_assign_hourly_stage':obj.flg_assign_hourly_stage,
        'flg_assign_fixed_price_stage':obj.flg_assign_fixed_price_stage,
        'flg_assign_other_exp_billable':obj.flg_assign_other_exp_billable,
        'flg_assign_court_proceed_billable':obj.flg_assign_court_proceed_billable})
        
        errstr = False
        invoice_line_obj = self.env['case.sheet.invoice.line']
        for case in obj.case_sheet_ids:
            ret = case.with_context(vals).invoice_case_sheet()
            if ('valid') in ret and not ret['valid']:
                errstr = errstr and errstr+', "'+ case.name +'"' or 'Nothing to Invoice for File Number(s) "'+ case.name +'"'
            invoice_obj = self.env['case.sheet.invoice'].browse(ret['res_id'])
            invoice_lines = {
                'inv_id_fixed': invoice_obj.invoice_lines_fixed,
                'inv_id_assignment_hourly': invoice_obj.invoice_lines_assignment_hourly,
                'inv_id_assignment_fixed': invoice_obj.invoice_lines_assignment_fixed,
                'inv_id_other_expense': invoice_obj.invoice_lines_other_expenses,
                'inv_id_court_proceed_fixed': invoice_obj.invoice_lines_court_proceedings_fixed,
                'inv_id_court_proceed_assignment': invoice_obj.invoice_lines_court_proceedings_assignment
                }
            for i in invoice_lines.keys():
                self.check_case_sheet(invoice_obj, invoice_lines[i], i)
        if errstr:
            raise UserError(_('%s' % errstr))
#         if not obj.name:
#             client_id = obj.client_id
#             number = self.env['ir.sequence'].get('consolidated.bill') or '/'
#             number = client_id.client_data_id+'/'+number or '/'
#         else:
#             number = obj.name
        number = self.env['ir.sequence'].next_by_code('account.invoice.consolidated') or '/'
        self.write({'state':'confirm'})
        if not self.name:
            self.write({'name':number})
        return True

    # @api.multi
    # def print_annexure(self):
    #     '''
    #     This function prints the Consolidated Bill
    #     '''
    #     datas = {
    #         'model': 'consolidated.bill',
    #         'ids': self.ids,
    #         'form': self.read(self.ids[0]),
    #         }
    #     invoice = self.ids[0]
    #     if invoice.invoice_template=='general':
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'consolidated.bill.annexure',
    #             'datas': datas,
    #             'name':'Annexure '+(self.read(self.ids[0],['name'])['name']),
    #             'nodestroy' : True
    #         }
    #     elif invoice.invoice_template=='india_llp':
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'consolidated.bill.llp.annexure',
    #             'datas': datas,
    #             'name':'Annexure '+(self.read(self.ids[0],['name'])['name']),
    #             'nodestroy' : True
    #         }
    #     elif invoice.invoice_template=='hdfc':
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'consolidated.bill.hdfc.annexure',
    #             'datas': datas,
    #             'name':'Annexure '+(self.read(self.ids[0],['name'])['name']),
    #             'nodestroy' : True
    #         }
    #     elif invoice.invoice_template=='cbi':
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'consolidated.bill.cbi.annexure',
    #             'datas': datas,
    #             'name':'Annexure '+(self.read(self.ids[0],['name'])['name']),
    #             'nodestroy' : True
    #         }
    #
    # @api.multi
    # def print_bill(self):
    #     '''
    #     This function prints the Consolidated Bill
    #     '''
    #     datas = {
    #              'model': 'consolidated.bill',
    #              'ids': self.ids,
    #              'form': self.read(self.ids[0]),
    #     }
    #     invoice = self.ids[0]
    #     if invoice.invoice_template=='general':
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'consolidated.bill',
    #             'datas': datas,
    #             'name':self.read(self.ids[0],['name'])['name'],
    #             'nodestroy' : True
    #         }
    #     elif invoice.invoice_template=='india_llp':
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'consolidated.bill.llp',
    #             'datas': datas,
    #             'name':self.read(self.ids[0],['name'])['name'],
    #             'nodestroy' : True
    #         }
    #     elif invoice.invoice_template=='hdfc':
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'consolidated.bill.hdfc',
    #             'datas': datas,
    #             'name':self.read(self.ids[0],['name'])['name'],
    #             'nodestroy' : True
    #         }
    #     elif invoice.invoice_template=='cbi':
    #         return {
    #             'type': 'ir.actions.report.xml',
    #             'report_name': 'consolidated.bill.cbi',
    #             'datas': datas,
    #             'name':self.read(self.ids[0],['name'])['name'],
    #             'nodestroy' : True
    #         }
        
    @api.multi
    def import_cases_consolidated(self):
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'wizard_update_import_cases_for_consolidated_bill_id')
        except ValueError as e:
            view_id = False
        return {
            'name':_("Import Case Sheets for Billing"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'consolidated.bulk.case.sheet',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            # 'context': context
        }            

ConsolidatedBill()


class ConsolidatedBillFollowup(models.Model):
    _name = 'consolidated.bill.followup'
    _description = 'Consolidated Bill Followup'
    _order = "date"

    @api.multi
    def _get_invoice_amount(self):
        res={}
        uid = SUPERUSER_ID
        for obj in self:
            res[obj.id] = obj.bill_id.amount_total
        return res

    @api.multi
    def _get_contact_person(self):
        res={}
        uid = SUPERUSER_ID
        for obj in self:
            contact_partner1_id = False
            for case_obj in obj.bill_id.case_sheet_ids:
                if case_obj.contact_partner1_id:
                    contact_partner1_id = case_obj.contact_partner1_id.id
                    break
            res[obj.id] = contact_partner1_id
        return res

    date= fields.Date('Date')
    name= fields.Text('Description')
    bill_id= fields.Many2one('consolidated.bill', 'Bill')
    create_date= fields.Datetime('Create Date')
    next_date= fields.Date('Next Date')
    state= fields.Selection([
        ('communicate', 'To Communicate'),
        ('communicated', 'Communicated'),
        ('completed', 'Completed')], 'Status')
    communicate_via= fields.Selection([
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('meeting', 'Meeting')], 'Communicated Via')
    client_service_manager_id= fields.Many2one('hr.employee',related='bill_id.client_service_manager_id', string='Client Relationship Manager', readonly=True)
    due_next_date_over= fields.Boolean('Due Date Over', default=False)
    partner_id= fields.Many2one('res.partner',related='bill_id.client_id', string='Client', readonly=True, store=True)

    invoice_date= fields.Date(related='bill_id.invoice_date', string='Invoice Date', readonly=True)
    division_id= fields.Many2one('hr.department',related='bill_id.division_id', string='Department', readonly=True)
    branch_id= fields.Many2one('ho.branch',related='bill_id.branch_id', string='Office', readonly=True)

    contact_partner1_id= fields.Many2one('res.partner',compute='_get_contact_person', string='Contact Person 1', readonly=True)
    due_days_string=fields.Char(related='bill_id.due_days_string', string='Aging', readonly=True)
    amount= fields.Float(compute='_get_invoice_amount', string='Amount')
    remark_id= fields.Many2one('legal.followup.remark', 'Followup Remarks')

    # _defaults = {
    #     'due_next_date_over':  False
    #     }
    
    @api.multi
    def write(self, vals):
        for follow_obj in self:
            if follow_obj.name == 'Missing Followup(System Generated Messages)' and vals.get('name', False):
                vals.update({'due_next_date_over': False})
        res = super(ConsolidatedBillFollowup, self).write(vals)
        return res

    @api.multi
    def bill_next_date_scheduler(self):
        followup_ids = self.search([('state', '=', 'communicate')])
        invoice_ids = [follow_obj.bill_id for follow_obj in followup_ids]
        if followup_ids:
            for invoice_obj in invoice_ids:
                if invoice_obj.next_followup_date and time.strftime('%Y-%m-%d') >= invoice_obj.next_followup_date:
                    for line in invoice_obj.bill_followup_ids:
                        if line.next_date == invoice_obj.next_followup_date:
                            # self.write(cr, uid, [line.id], {'due_next_date_over': True}, context=context)
                            line.write({'due_next_date_over': True})
                        else:
                            if line.name != 'Missing Followup(System Generated Messages)':
                                # self.write(cr, uid, [line.id], {'due_next_date_over': False}, context=context)
                                line.write({'due_next_date_over': False})
        followup_ids = self.search([('state', '!=', 'communicate'),('due_next_date_over', '=', True)])
        # self.write(followup_ids, {'due_next_date_over': False})
        followup_ids.write({'due_next_date_over': False})
        return True

ConsolidatedBillFollowup()

class ConsolidatedBillLine(models.Model):
    _name = "consolidated.bill.line"
    _description = "Consolidated Bill Particulars"

    inv_id_bill=fields.Many2one('consolidated.bill','Consolidated Bill ID')
    name= fields.Char('Description')
    amount=fields.Float('Amount')

    @api.onchange('invid')
    def onchange_line_amount(self):
        context = self._context or {}
        val = {}
        obj = self.browse(self.invid)
        line_total = 0.00
        for line in obj.invoice_lines:            
            line_total= line_total + line.amount
        if round(line_total,2) != round(obj.amount_total,2):
            val['amount'] = 0.00
            raise UserError(_('Total Amount in Billing Particulars is NOT EQUAL to Total Amount!'))
        
        return {'value':val}

ConsolidatedBillLine()


class UpdateBill(models.TransientModel):
    _name = "update.bill"
    _description = "Update Consolidated Bill Particulars"

    @api.model
    def default_get(self, fields):
        print ("fieldsfields",fields)
        if self._context is None: context = {}
        res = super(UpdateBill, self).default_get(fields)
        bill_id_ids = self._context.get('active_ids', [])
        active_model = self._context.get('active_model')
        bill_id = bill_id_ids
        if 'bill_id' in fields:
            res.update(bill_id=bill_id)
        if 'particular_ids' in fields:
            bill_obj = self.env['consolidated.bill'].browse(bill_id)
            particulars = [self._particular_for(m) for m in bill_obj.invoice_lines]
            res.update(particular_ids=[(0,0,particulars[0])])
        print ("res--------------",res)
        return res
    
    @api.multi
    def _particular_for(self,line):
        particular = {
            'name' : line.name,
            'amount' : line.amount,
            }
        return particular

    particular_ids= fields.One2many('update.bill.line', 'wizard_id', 'Consolidated Bill Lines')
    bill_id= fields.Many2one('consolidated.bill', 'Bill', ondelete='CASCADE')

    
    @api.multi
    def update_particulars(self):
        for data in self:
            line_ids = [line.id for line in data.bill_id.invoice_lines]
            invoice_ids = [line.invoice_id.id for line in data.bill_id.case_invoice_lines]
            self.env.cr.execute('delete from consolidated_bill_line where id IN %s', (tuple(line_ids),))
            self.env.cr.execute('delete from particular_account_invoice_line where invoice_id IN %s', (tuple(invoice_ids),))
            amount = 0.00
            name = ''
            for line in data.particular_ids:
                name +=   line.name + ','
                amount += line.amount
                self.env['consolidated.bill.line'].create({
                    'name': line.name, 
                    'amount': line.amount, 
                    'inv_id_bill': data.bill_id.id
                    })
            if amount != data.bill_id.amount_total:
                raise UserError(_('Total amount must be same as consolidated bill amount'))
            
            for invoice_line in data.bill_id.case_invoice_lines:
                
                self.env['particular.account.invoice.line'].create({
                    'name': name, 
                    'price_unit': invoice_line.amount_total_1, 
                    'invoice_id': invoice_line.invoice_id.id
                    })
        return True

UpdateBill()


class UpdateBillLine(models.TransientModel):
    _name = "update.bill.line"
    _description = "Update Consolidated Bill Particulars Line"

    wizard_id= fields.Many2one('update.bill', string="Wizard", ondelete='CASCADE')
    name= fields.Char('Description')
    amount=fields.Float('Amount')

UpdateBillLine()


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        res = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            if voucher.consolidated_id:
                for consolidated_id in voucher.consolidated_id:
                    count = 0
                    lines = []
                    if consolidated_id.case_invoice_lines:
                        count = len(consolidated_id.case_invoice_lines)
                        for line in consolidated_id.case_invoice_lines:
                            if line.invoice_id and line.invoice_id.state == 'paid':
                                lines.append(line)
                    if count == len(lines):
                        self.env['consolidated.bill'].write( [consolidated_id.id], {'state': 'paid', 'partially_paid': False})
                    else:
                        self.env['consolidated.bill'].write([consolidated_id.id], {'partially_paid': True})
                    
        return res

    @api.multi
    def cancel_voucher(self):
        res = super(AccountVoucher, self).cancel_voucher()
        for voucher in self:
            if voucher.consolidated_id:
                for consolidated_id in voucher.consolidated_id:
                    count = 0
                    lines = []
                    if consolidated_id.case_invoice_lines:
                        count = len(consolidated_id.case_invoice_lines)
                        for line in consolidated_id.case_invoice_lines:
                            if line.invoice_id and line.invoice_id.state != 'paid':
                                lines.append(line)
                    if count == len(lines):
                        self.env['consolidated.bill'].write([consolidated_id.id], {'state': 'invoice'})
        return True

AccountVoucher()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: