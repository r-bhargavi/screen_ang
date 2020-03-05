# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
import odoo.addons.decimal_precision as dp
import urllib.parse
from werkzeug import url_encode
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)

line_count_slno = 0

_TASK_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled'), ('hold', 'Hold')]

account_codes = [[4250,205651],[50000,2054228],[10000,2054081],[10000,2054288],[777500,2054059],[17500,2054059],[202013,2054154],[6050100,205597],[180000,2054074],[227500,205599],[37500,2054166],[60000,2054061],[12000,2054089],[50000,2054059],[15000,2054129],[50000,1001],[13467,2054019],[100000,2054065],[250000,2054044],[62500,2054279],[31900,205599],[23180,205602],[100000,2054005],[175000,2054017],[15000,2054272],[6875,205651],[15000,2054069],[495159,2054040],[2040,2054074],[6250,205604],[8000,2054081],[3355340,2054055],[37500,2054159],[120000,2054024],[44250,205597],[50750,205597],[14000,205597],[8750,205597],[50000,2054155],[40000,2054173],[20000,2054191],[22500,2054271],[44500,2054275],[30000,2054139],[50000,2054236],[50000,2054168],[20000,2054174],[20000,2054103],[75400,2054061],[256500,2054323],[50000,2054209],[8000,205526],[20000,2054002],[21000,205651],[20000,2054176],[20000,2054177],[60000,2054051],[15000,2054321],[20000,2054178],[20000,2054197],[20000,2054179],[180000,2054172],[20000,2054180],[3000,2054059],[17000,2054110],[40000,2054093],[20000,2054181],[85000,2054130],[25000,2054003],[5000,2054316],[250000,205553],[50000,1001],[20000,2054182],[80000,2054183],[345000,2054039],[20000,205565],[100000,2054212],[20000,2054117],[500,205572],[215000,2054203],[30000,2054111],[277500,2054234],[20000,2054184],[25000,2054185],[793037,2054019],[35000,2054041],[50000,2054308],[20000,205584],[795860,205586],[20000,2054286],[35000,2054044],[622250,205597],[134000,205599],[60000,205602],[11850,205604],[116000,2054005],[50000,2054277],[20000,2054187],[100000,2054113],[25000,2054188],[20000,2054189],[100000,205611],[20000,2054190],[233000,2054001],[60000,2054200],[50000,2054063],[25000,2054099],[55000,205597],[6250,205604],[33625,205651],[5000,205572],[250000,2054027],[71500,2054039],[12000,2054228],[195000,2054061],[23500,2054139],[150000,2054033],[8000,2054123],[85000,2054101],[30000,2054114],[62000,2054117],[275000,2054019],[52500,205586],[12000,2054286],[655500,205599],[290000,2054001],[56000,2054228],[5000,205651],[30000,205599],[52200,2054228],[62500,2054228],[90000,2054228],[10000,2054089],[6500,2054005],[60000,2054061],[7500,2054123],[89500,205599],[8000,205602],[75000,2054142]]


class CourtLocation(models.Model):
    _name = 'court.location'

    name=fields.Char('Location Name',size=1024,required=True)

CourtLocation()


class CaseSheet(models.Model):
    _name = 'case.sheet'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = 'Case Sheet Details'

    @api.multi
    def search(self, args, offset=0, limit=None, order=None,count=False):
        if self._context is None:
            context = {}
        if self._context.get('case_sheet', False):
            if self.env['res.users'].has_group('legal_e.group_legal_e_lawyers') and self.env.user.id != SUPERUSER_ID:
                args += [('members', 'in', [self.env.user.id])]
        return super(CaseSheet, self).search(args, offset, limit, order, count)

    @api.multi
    def update_task_line(self):
        case_pool = self.env['case.sheet']
        office_pool = self.env['ho.branch']
        fixed_pool = self.env['fixed.price.stages']
        case_tasks_pool = self.env['case.tasks.line']
        task_pool = self.env['task.master']
        case_ids = [13538,13539,13540,13541,13542,13543,13544,13545,13546,13547,13549,13550,13551,13552,13553,13554,13555,13556,13557,13558,13559,13560,13561,13562,13563,13565,13566,13567,13568,13569,13570,13571,13572,13573,13574,13575,13576,13577,13578,13579,13580,13581,13582,13583,13584,13585,13586,13587,13588,13589,13590,13591,13592,13593,13594,13595,13596,13597,13598,13599,13600,13601,13602,13603,13605,13606,13607,13611,13612,13613,13614,13615,13617,13618,13619,13620,13621,13622,13623,13624,13625,13439,13440,13442,13444,13445,13446,13447,13449,13454,13456,13457,13458,13460,13461,13462,13463,13464,13465,13467,13469,13470,13472,13473,13475,13476,13477,13478,13479,13480,13483,13484,13485,13487,13488,13489,13490,13491,13492,13493,13494,13495,13496,13497,13498,13499,13500,13502,13503,13504,13506,13508,13509,13510,13511,13513,13515,13517,13520,13521,13523,13524,13525,13528,13529,13530,13531,13532,13533,13534,13535,13536,13537,13655,13656,13657,13658,13659,13660,13661,13662,13663,13664,13665,13666,13667,13668,13669,13670,13671,13672,13673,13674,13675,13676,13677,13678,13679,13680,13681,13682,13683,13684,13685,13686,13687,13688,13689,13690,13691,13692,13693,13694,13695,13696,13697,13698,13699,13700,13701,13702,13704,13705,13706,13707,13708,13709,13710,13711,13712,13713,13715,13716,13717,13718,13719,13720,13721,13722,13723,13724,13725,13726,13727,13730,13731,13732,13733,13734,13735,13736,13737,13738,13739,13740,13741,13742,13743,13744,13745,13746,13747,13748,13749,13750,13751,13752,13753,13754,13755,13756,13757,13758,13759,13760,13761,13762,13763,13764,13765,13766,13767,13768,13769,13770,13771,13772,13773,13774,13775,13776,13777,13778,13779,13780,13781,13782,13784,13785,13786,13787,13788,13789,13790,13791,13792,13793,13794,13795,13796,13797,13798,13799,13800,13801,13802,13803,13804,13805,13806,13807,13808,13809,13810,13811,13812,13813,13814,13815,13816,13817,13818,13819,13820,13821,13822,13823,13824,13825,13826,13827,13828,13829,13830,13831,13832,13833,13834,13835,13836,13837,13838,13839,13840,13842,13843,13844,13845,13846,13847,13848,13850]
        case_ids = list(set(case_ids))
        case_tasks_ids = case_tasks_pool.search([('name', '=', 48)])
        if case_tasks_ids:
            fixed_ids = fixed_pool.search([('name', 'in', case_tasks_ids),('office_id', '=', 45), ('amount','=', 1825), ('case_id', 'not in', case_ids)])
            for fixed_line_obj in fixed_ids:
                    fixed_pride = fixed_line_obj.case_id.fixed_price
                    tot = 0.0
                    for line_obj in fixed_line_obj.case_id.stage_lines:
                        if line_obj.id not in fixed_ids:
                            tot += line_obj.amount + line_obj.out_of_pocket_amount
                    diff = fixed_pride - tot
                    if diff:
                        fixed_pool.write([fixed_line_obj.id], {'amount': diff})
        return True

    @api.multi
    def account_line_create(self):
        acct_code = {}
        for accts in account_codes:
            if accts[1] in acct_code:
                acct_code[accts[1]] += accts[0]
            else:
                acct_code[accts[1]] = accts[0]
        for account in acct_code.keys():
            account_ids = self.env['account.account'].search([('code', '=', account)])
            if account_ids:
                account_obj = (account_ids[0])
                # account_obj = self.env['account.account'].browse(account_ids[0])
                field_names = ['credit', 'debit', 'balance']
                context = {'lang': 'en_US', 'tz': 'Asia/Kolkata', 'uid': 1, 'active_model': 'account.chart', 'state': 'all', 'periods':  [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],  'fiscalyear': 2}
                res = self.env['account.account'].compute(account_ids, field_names, None,  '', ())
        return True

    @api.multi
    def _get_court_no(self):
        res = []
        for i in range(50):
            i += 1
            res.append((str(i), str(i)))
        return res

    # Starting set bill_state field // Sanal Davis // 5-6-15
    @api.depends('bill_type', 'bill_state', 'stage_lines.invoiced', 'fixed_price')
    def _get_bill_state(self):
        for case in self:
            val = 'not_billed'
            invoiced_state = []
            total_amount = 0.00
            if case.bill_type == 'fixed_price':
                for line in case.stage_lines:
                    if line.invoiced:
                        invoiced_state.append(line.id)
                    total_amount += (line.amount + line.out_of_pocket_amount)
                if case.state in ('new', 'cancel', 'transfer'):
                    val = 'not_billed'
                else:
                    if case.stage_lines and invoiced_state and total_amount and case.fixed_price:
                        if len(case.stage_lines) == len(invoiced_state):
                            if total_amount >= case.fixed_price:
                                val = 'fully_billed'
                            else:
                                val = 'partial_billed'
                        elif invoiced_state and len(case.stage_lines) > len(invoiced_state):
                            val = 'partial_billed'
                        elif not invoiced_state:
                            val = 'not_billed'
            else:
                if case.state == 'done':
                    val = 'fully_billed'
                else:
                    billed = False
                    for line in case.assignment_fixed_lines:
                        if line.invoiced:
                            billed = True
                    for line in case.assignment_hourly_lines:
                        if line.billed_hours:
                            billed = True
                    if billed:
                        val = 'partial_billed'
            case.bill_state = val
        return case

    @api.multi
    def _get_unbilled_amount(self):
        for case_obj in self:
            unbilled_amount = 0.00
            for fixed_obj in case_obj.stage_lines:
                if not fixed_obj.invoiced:
                    unbilled_amount += fixed_obj.amount + fixed_obj.out_of_pocket_amount

            for expense_obj in case_obj.other_expenses_lines:
                if not expense_obj.invoiced and expense_obj.billable == 'bill':
                    unbilled_amount += expense_obj.amount

#             for associate_obj in case_obj.associate_payment_lines:
#                 if not associate_obj.invoiced:
#                     unbilled_amount += associate_obj.amount

            for ass_hour_obj in case_obj.assignment_hourly_lines:
                if not ass_hour_obj.invoiced:
                    unbilled_amount += ass_hour_obj.amount * ass_hour_obj.billed_hours

            for ass_fix_obj in case_obj.assignment_fixed_lines:
                if not ass_fix_obj.invoiced:
                    unbilled_amount += ass_fix_obj.amount +  ass_fix_obj.out_of_pocket_amount
            case_obj.unbilled_amount = unbilled_amount
        return True

    @api.depends('stage_lines')
    def _get_billed_amount(self):
        for case_obj in self:
            billed_amount = received_amount = spent_amount = 0.00
            for fixed_obj in case_obj.stage_lines:
                if fixed_obj.invoiced:
                    billed_amount += fixed_obj.amount + fixed_obj.out_of_pocket_amount

            for expense_obj in case_obj.other_expenses_lines:
                if expense_obj.invoiced and expense_obj.billable == 'bill':
                    billed_amount += expense_obj.amount

#             for associate_obj in case_obj.associate_payment_lines:
#                 if associate_obj.invoiced:
#                     billed_amount += associate_obj.amount

            for ass_hour_obj in case_obj.assignment_hourly_lines:
                    billed_amount += ass_hour_obj.amount * ass_hour_obj.billed_hours

            for ass_fix_obj in case_obj.assignment_fixed_lines:
                    billed_amount += ass_fix_obj.amount * ass_fix_obj.billed_hours
            case_obj.billed_amount =  billed_amount
            # res[case_obj.id] =  billed_amount
        return case_obj

    @api.depends('stage_lines')
    def _get_received_amount(self):
        for case_obj in self:
            received_amount = 0.0
            invoice_ids = self.env['account.invoice'].search([('state','not in',['draft','cancel']),('type','in',['out_invoice',]),('case_id', '=', case_obj.id)])
            for invoice_obj in invoice_ids:
            # for invoice_obj in self.env['account.invoice'].browse(SUPERUSER_ID, invoice_ids):
                paid_amount = invoice_obj.amount_total - invoice_obj.residual
                received_amount += paid_amount
            case_obj.received_amount = received_amount
            # res[case_obj.id] = received_amount
        return case_obj

    @api.depends('other_expenses_lines')
    def _get_spent_amount(self):
        # account_ids = [account_obj.id for account_obj in self.env['res.users'].browse(SUPERUSER_ID).company_id.expense_account_ids]
        for case_obj in self:
            spent_amount = 0.0
            line_ids = self.env['account.move.line'].search([('account_id.user_type_id.name', '=', 'Expense'),('case_id', '=', case_obj.id),('debit', '!=', False)])
            for line_obj in line_ids:
                spent_amount += line_obj.debit
            # for associate_obj in case_obj.associate_payment_lines:
            #     if associate_obj.invoiced:
            #         spent_amount += associate_obj.amount
            case_obj.spent_amount = spent_amount
            # for expense_obj in case_obj.other_expenses_lines:
            #     spent_amount += expense_obj.paid_amount
            #     # if expense_obj.invoiced and expense_obj.billable == 'bill':
            #     #     spent_amount += expense_obj.paid_amount
            # case_obj.spent_amount = spent_amount
        return case_obj

    @api.multi
    def _get_stage_case_ids(self):
        line_obj = self.env['fixed.price.stages']
        return [line.case_id.id for line in line_obj]

    @api.multi
    def _get_expense_case_ids(self):
        result = {}
        for line in self:
            result[line.case_id.id] = True
        return result.keys()

    @api.multi
    def _get_assignment_case_ids(self):
        result = {}
        for line in self:
            if line.case_fixed_id:
                result[line.case_fixed_id.id] = True
            elif line.case_hourly_id:
                result[line.case_hourly_id.id] = True
        return result.keys()

    @api.multi
    def _get_associate_case_ids(self):
        result = {}
        for line in self:
            result[line.case_id.id] = True
        return result.keys()

    @api.depends('stage_lines')
    def _get_out_standing_amount(self):
        for obj in self:
            outstand = 0.00
            reids = self.env['case.sheet.invoice'].search([('case_id','=',obj.id)])
            for line in reids:
                if line.invoice_id and line.invoice_id.state in ('draft','open'):
                    outstand += line.invoice_id.residual
            obj.outstanding_amount = outstand
        return True

    @api.depends('first_parties','opp_parties')
    def _get_first_opposite_party(self):
        # res = {}
        for case_obj in self:
            # res[case_obj.id] = {
            #     'first_party': '',
            #     'opposite_party': '',
            #
            #     }
            if case_obj.first_parties:
                type = self.env['first.parties.details'].get_selection_value('type' , case_obj.first_parties[0].type)
                case_obj.first_party = case_obj.first_parties[0].name + '(' + type + ')'
                # res[case_obj.id]['first_party'] = case_obj.first_parties[0].name + '(' + type + ')'

            if case_obj.opp_parties:
                type = self.env['opp.parties.details'].get_selection_value('type' , case_obj.opp_parties[0].type)
                case_obj.opposite_party = case_obj.opp_parties[0].name + '(' + type + ')'
                # res[case_obj.id]['opposite_party'] = case_obj.opp_parties[0].name + '(' + type + ')'
        # return res

    def _get_first_part_case_ids(self):
        result = {}
        for line in self.ids:
            result[line.party_id.id] = True
        return result.keys()

    @api.multi
    def _get_opp_part_case_ids(self):
        result = {}
        for line in self.ids:
            result[line.party_id.id] = True
        return result.keys()

    @api.onchange('department_ids')
    def _get_assignee_ids(self):
        assignee = []
        if self.department_ids:
            for dept in self.department_ids:
                emp = self.env['hr.employee'].search([('department_id', '=', dept.id)])
                for employee in emp:
                    assignee.append(employee.id)
            return {
                'domain': {'assignee_id': [('id', 'in', assignee)]}
            }
    @api.onchange('division_id_new')
    def _get_assignee_id_new(self):
        assignee = []
        if self.division_id_new:
            dept = self.env['hr.department'].search([('id', '=', self.division_id_new.id)])
            assignee.append(dept.manager_id.id)
            return {
                'domain': {'assignee_id_new': [('id', 'in', assignee)]}
            }
    @api.onchange('division_id')
    def _get_assignee_id(self):
        assignee = []
        if self.division_id:
            dept = self.env['hr.department'].search([('id', '=', self.division_id.id)])
            assignee.append(dept.manager_id.id)
            return {
                'domain': {'assignee_id': [('id', 'in', assignee)]}
            }

    name= fields.Char(string='File Number', size=64, required=False, readonly=False, track_visibility='always', defaultl=lambda obj: '/')
    date=fields.Date(string='Date' , track_visibility='onchange', default=lambda *a: time.strftime('%Y-%m-%d'))
    company_ref_no=fields.Char(string='Client Ref #',size=40, track_visibility='onchange')
    group_val=fields.Selection([('individual','INDIVIDUAL'),('proprietary','PROPRIETARY'),('company','COMPANY'),('firm','FIRM'),('llp','LLP'),('trust','TRUST'),('bank','BANK'),('others','OTHERS')],string='Group', track_visibility='onchange')
    client_id= fields.Many2one('res.partner',string='Client Name', required=True, track_visibility='onchange')
    contact_partner1_id= fields.Many2one('res.partner',string='Contact Person 1', track_visibility='onchange')
    contact_partner2_id=fields.Many2one('res.partner',string='Contact Person 2', track_visibility='onchange')
    work_type=fields.Selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], string='Type of Work', required=True, track_visibility='onchange')
    court_district_id= fields.Many2one('district.district',string='Court District', track_visibility='onchange')
    court_location_id= fields.Many2one('court.location',string='Court Location', track_visibility='onchange')
    court_id=fields.Many2one('court.master',string='Court Name', track_visibility='onchange')
    no_court=fields.Boolean(string='No Court')
    arbitrator_id= fields.Many2one('arbitrator.master',string='Arbitrator', track_visibility='onchange')
    mediator_id= fields.Many2one('mediator.master',string='Mediator', track_visibility='onchange')
    assignee_id= fields.Many2one('hr.employee',string='Assignee', track_visibility='onchange')
    other_assignee_id= fields.Many2one('res.partner',string='External Other Associate', track_visibility='onchange')
    other_assignee_ids=fields.One2many('other.associate','case_id',string='External Other Associate(s)')
    connected_matter= fields.Text(string='Connected Matter', track_visibility='onchange')
    casetype_id=fields.Many2one('case.master',string='Case Type', required=True, track_visibility='onchange')
    litigation_type = fields.Selection([
        ('lumpsum', 'Lumpsum'), ('appearance_wise', 'Appearance-wise')], 'Type of Litigation')
    nonlitigation_type = fields.Selection([
        ('fixed', 'Fixed / Lumpsum'), ('per_hour', 'Per Hour')], 'Type of Nonlitigation')
    our_client=fields.Selection([('first','First Party'),('opposite','Opposite Party')],string='Client Position', track_visibility='onchange')
    lodging_number=fields.Char(string='Lodging Number', track_visibility='onchange')
    lodging_date=fields.Date(string='Lodging Date', track_visibility='onchange')
    reg_number=fields.Char(string='Case No.', track_visibility='onchange')
    reg_date=fields.Date(string='Case Date', track_visibility='onchange')
    tasks_lines= fields.One2many('case.tasks.line', 'case_id', string='Assignee Tasks',copy=True)
    associate_tasks_lines= fields.One2many('associate.tasks.line', 'case_id',string= 'Associate Tasks',copy=True)
    other_expenses_lines=fields.One2many('other.expenses', 'case_id',string= 'Other Expenses', copy=False)
    client_tasks_lines= fields.One2many('client.tasks.line', 'case_id',string= 'Client Tasks',copy=True)
    associate_payment_lines=fields.One2many('associate.payment', 'case_id', string='Associate Payment Lines')
    first_parties=fields.One2many('first.parties.details','party_id',string='First Party Lines',copy=True)
    opp_parties=fields.One2many('opp.parties.details','party_id',string='Opposite Party Lines', copy=False)
    bill_type=fields.Selection([('fixed_price','Fixed Price'),('assignment_wise','Assignment Wise')],string='Billing Type', required=False, track_visibility='onchange')
    fees_lines=fields.One2many('fee.info.line', 'case_id', string='Fees Information')
    stage_lines=fields.One2many('fixed.price.stages','case_id',string='Fixed Price Stages',copy=True)
    fixed_price=fields.Float(string='Fixed Price Amount', track_visibility='onchange', copy=False)
    assignment_hourly_lines=fields.One2many('assignment.wise','case_hourly_id',string='Assignment Wise Hourly Lines',copy=True)
    assignment_fixed_lines=fields.One2many('assignment.wise','case_fixed_id',string='Assignment Wise Fixed Lines',copy=True)
    total_projected_amount=fields.Float(string='Total Projected Amount', track_visibility='onchange')
    assignment_approval_date=fields.Date(string='Approval Date' , track_visibility='onchange')
    effective_court_proceed_amount=fields.Float(string='Effective Court Proceedings Amount', track_visibility='onchange')
    non_effective_court_proceed_amount=fields.Float(string='Non-Effective Court Proceedings Amount', track_visibility='onchange')
    project_id=fields.Many2one('project.project',string='Project ID')
    # branch_id=fields.Many2one('sale.shop','Branch', required=False)
    state = fields.Selection([
        ('new', 'New'),
        ('waiting', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('cancel', 'Cancelled'),
        ('transfer', 'Transferred'),
        ('won', 'Won'),
        ('arbitrated', 'Arbitrated'),
        ('withdrawn', 'With Drawn'),
        ('lost', 'Lost'),
        ('inactive', 'Inactive'),
        ('hold', 'Hold'),
        ('done', 'Closed'),
        ('waiting_assignee', 'Waiting for Assignee Approval'),
        ('waiting_accounts', 'Waiting for Accounts Approval'),
        ('waiting_admin', 'Waiting for Admin Approval'),
        ('sheet_rejected', 'Case Sheet Rejected'),
        ('closure_rejected', 'Closure Rejected'),
    ], string='Status', readonly=True, track_visibility='onchange', default='new')
    inward_register=fields.One2many('inward.register','file_number',string='Inward Register')
    outward_register= fields.One2many('outward.register','file_number',string='Outward Register')
    court_proceedings=fields.One2many('court.proceedings','case_id',string='Court Proceedings', copy=False)
    case_close = fields.Boolean(string='Is Case Closure Request', default=False)
    close_date=fields.Date(string='Close Date', track_visibility='onchange')
    close_comments=fields.Char(string='Close Comments', track_visibility='onchange',copy=False)
    closure_type = fields.Selection([('return', 'Return'), ('retain', 'Retain'), ('destroy', 'Destroy')],
                                    'Closure Type', track_visibility='onchange')
    time_duration = fields.Selection([('1month', '1 Month'), ('3month', '3 Months'), ('6month', '6 Months'),
                                      ('12month', '12 Months')], 'Time Duration', track_visibility='onchange')
    approve_closure_date = fields.Date(string='Case Closure Date', track_visibility='onchange')
    assignee_case_closure_reject=fields.Char(string='Assignee Case Closure Reject Reason')
    accounts_case_closure_reject=fields.Char(string='Accounts Case Closure Reject Reason')
    admin_case_closure_reject=fields.Char(string='Admin Case Closure Reject Reason')
    cancel_comments=fields.Text(string='Cancel Comments')
    cancel_date=fields.Date(string='Cancel Date', track_visibility='onchange')
    state_id=fields.Many2one('res.country.state', string='State', track_visibility='onchange')
    zone_id=fields.Many2one('state.zone', string='Zone')
    district_id=fields.Many2one('district.district', string='Assignee District', track_visibility='onchange')
    district_id_associate=fields.Many2one('district.district',string='Associate District')
    location=fields.Char(string='Location')
    division_id=fields.Many2one('hr.department', string='Department/Division', track_visibility='onchange', ondelete="restrict", required=True)
    #new field
    division_id_new=fields.Many2one('hr.department', string='Department/Division', track_visibility='onchange', ondelete="restrict")
    assignee_id_new= fields.Many2one('hr.employee',string='Assignee', track_visibility='onchange')

    primary_id=fields.Many2one('case.sheet','Primary Case')
    department_ids=fields.Many2many('hr.department', 'case_sheet_hr_department_relation','case_id','department_id' ,string='Department/Division', track_visibility='onchange', ondelete="restrict", required=True)
    ho_branch_id=fields.Many2one('ho.branch',string='Location', track_visibility='onchange', ondelete="restrict", required=True,copy=True)
    # parent_id_manager=fields.related('assignee_id', 'parent_id', type='Many2one', relation='hr.employee', string="Manager", store=False)
    parent_id_manager=fields.Many2one('hr.employee', related='assignee_id.parent_id', string='Manager', store=False)
    transfer_location_id=fields.Many2one('ho.branch',string='Transferred Location')
    transfer_file_number= fields.Char(string='Transferred File Number')
    transfer_file_number_id= fields.Many2one('case.sheet',string='Transferred File Number')
    outstanding_amount=fields.Float(compute='_get_out_standing_amount',string='Out-Standing Amount')
    company_id=fields.Many2one('res.company',string='Company', default=lambda self: self.env.user.company_id)
    client_service_executive_id=fields.Many2one('hr.employee',string='Client Service Manager', track_visibility='onchange')
    client_service_manager_id= fields.Many2one('hr.employee',string='Client Relationship Manager', track_visibility='onchange')
    region = fields.Selection([('north', 'North'), ('east', 'East'), ('west', 'West')], string='Region', store=True, related='state_id.region')
    #Add billed field // Sanal Davis // 5-6-15

    # bill_state=fields.function(_get_bill_state, string='Billed', type='selection', selection=[('none','/'), ('not_billed','Not Billed'),('partial_billed','Partially Billed'),('fully_billed','Fully Billed')],
    #                                 store = {
    #                                     'case.sheet': (lambda self, cr,uid,ids,c: ids, ['stage_lines','fixed_price', 'bill_type', 'assignment_fixed_lines', 'assignment_hourly_lines', 'state'], 10),
    #                                     'fixed.price.stages': (_get_stage_case_ids, ['amount', 'state', 'invoiced'], 10),
    #                                     'assignment.wise': (_get_assignment_case_ids, ['amount', 'billed_hours', 'remaining_hours','hours_spent', 'invoiced', 'state'], 10),
    #                                   }),
    bill_state = fields.Selection([('none', '/'), ('not_billed', 'Not Billed'), ('partial_billed', 'Partially Billed'),('fully_billed', 'Fully Billed')], string='Billed', compute='_get_bill_state')
    lot_name= fields.Char(string='Lot Number', size=64, readonly=True, track_visibility='onchange')
    show_billing= fields.Boolean(string='Show Billing')
    estimated_time= fields.Integer(string='Estimated Time')
    estimated_month=fields.Integer(string='Estimated Months')
    estimated_hearing= fields.Integer(string='Estimated Hearings')
    # refered_by= fields.Selection([('employee', 'Employee'), ('partner', 'Partner')], string='Refered By')
    # employee_id= fields.Many2one('hr.employee',string= 'Employee')
    partner_id= fields.Many2one('res.partner', string='Partner')
    # employee_partner_id= fields.Many2one('hr.employee', string='Partner1')
    referral_type = fields.Selection([('ref_emp', 'Refer by Employee'), ('ref_part', 'Refer by Partner'),
                                      ('ref_ext', 'Refer by External')], string="Referral Type")
    response_person = fields.Many2one('res.partner', 'Response Person')
    response_person_emp = fields.Many2one('hr.employee', 'Response Person')
    connected_case_sheet = fields.Many2one('case.sheet', 'Connected Case Sheet')
    referral_ref = fields.Char(string='External Reference')
    referral_specification = fields.Selection(
        [('matter_specific', 'Matter Specific'), ('client_specific', 'Client Specific')],
        string="Referral Specification")
    referral_validity = fields.Date('Referral Validity')
    referral_percentage = fields.Float('Referral Percentage')
    referral_amount = fields.Float('Referral Amount')
    arbitration_amount= fields.Float(string='Arbitration Fee', track_visibility='onchange')
    billed_amount = fields.Float(compute='_get_billed_amount', string='Billed Amount')
    spent_amount = fields.Float(compute='_get_spent_amount', string='Spent Amount')
    received_amount = fields.Float(compute='_get_received_amount', string='Received Amount')
    # 'opposite_party': fields.function(_get_first_opposite_party, type='char', string='Opposite Party', multi="party", store={
    #                                     'case.sheet': (lambda self, cr, uid, ids, c={}: ids, ['opp_parties'], 10),
    #                                     'opp.parties.details': (_get_opp_part_case_ids, ['name', 'sl_no'], 10),
    #                                     }),
    opposite_party = fields.Char(compute='_get_first_opposite_party', string='Opposite Party', store=True, copy=False)
    # 'first_party': fields.function(_get_first_opposite_party, type='char', string='First Party', multi="party", store={
    #                                     'case.sheet': (lambda self, cr, uid, ids, c={}: ids, ['first_parties'], 10),
    #                                     'first.parties.details': (_get_first_part_case_ids, ['name', 'sl_no'], 10),
    #                                     }),
    first_party = fields.Char(compute='_get_first_opposite_party', string='First Party', store=True, copy=False)
    members= fields.Many2many('res.users', 'case_user_rel', 'case_id', 'uid', string='Case Members')

    active = fields.Boolean('Active', default=True)
    assignment_history= fields.One2many('case.assignment.history','case_id',string='Assignment History', copy=False)
    # court_no= fields.Selection(compute='_get_court_no', string='Court No.', track_visibility='onchange')

    # unbilled_amount=fields.function(_get_unbilled_amount, type='Float', string='Unbilled Amount')
    unbilled_amount = fields.Float(compute='_get_unbilled_amount', string='Unbilled Amount')
    reject_comment = fields.Char(string='Reject Comment', track_visibility='onchange')
    hearing_type = fields.Selection([('hearing_wise', 'Hearing Wise Billing'), ('hearing_limit', 'Limit on Hearing Billing'), ('lumpsum', 'Lumpsum')],
                                    string="Hearing Type", required=True, default='hearing_limit')
    # effective_hearing_cost = fields.Float(string='Effective Hearing Cost', required=True)
    # non_effective_hearing_cost = fields.Float(string='Non Effective Hearing Cost', required=True)
    limit_on_hearing = fields.Integer(string='Limit on Hearing')
    we_thank_you = fields.Text(string='Initial Lines in SOW')
    scope_of_work = fields.Text(string='Scope of Work')
    annexure_one = fields.Text(string='Annexure 1')
    annexure_three = fields.Text(string='Annexure 3')
    upon_assignment = fields.Float(string='Upon Assignment',copy=False)
    upon_filing_complaint = fields.Float(string='Upon Filing complaint',copy=False)
    disposal = fields.Float(string='Upon Admission/Disposal/Withdrawal',copy=False)
    upon_admission = fields.Float(string='Upon Admission',copy=False)
    upon_filing_statement = fields.Float(string='Upon Written statement/Reply',copy=False)
    appearance_charges = fields.Float(string='Appearance billing',copy=False)
    effective_appearance = fields.Float(string='Effective Appearance/ hearing billing',copy=False)
    non_effective_appearance = fields.Float(string='Non- Effective Appearance/ hearing billing',copy=False)
    u1 = fields.Float(string='Upon Filing Writ Petition',copy=False)
    u2 = fields.Float(string='Upon filing Criminal Application',copy=False)
    u3 = fields.Float(string='Upon filing Reply',copy=False)
    u4 = fields.Float(string='Upon drafting FIR',copy=False)
    u5 = fields.Float(string='Upon Disposal',copy=False)
    u6 = fields.Float(string='Upon filing Police Complaint',copy=False)
    u7 = fields.Float(string='Upon Lodging Complaint/FIR before Police Station',copy=False)
    u8 = fields.Float(string='Upon filing of SOC',copy=False)
    u9 = fields.Float(string='Upon Rejoinder',copy=False)
    u10 = fields.Float(string='Upon filing Evidence',copy=False)
    u11 = fields.Float(string='Upon Award',copy=False)
    u12 = fields.Float(string='Upon filing defense Evidence',copy=False)
    u13 = fields.Float(string='Upon Disposal/Award',copy=False)
    u14 = fields.Float(string='Upon Filing',copy=False)
    u15 = fields.Float(string='Upon filing Claim',copy=False)
    u16 = fields.Float(string='Upon filing Application',copy=False)
    u17 = fields.Float(string='Upon Disposal/Withdrawal',copy=False)
    u18 = fields.Float(string='Upon filing Petition',copy=False)
    u19 = fields.Float(string='Upon Opinion',copy=False)
    u20 = fields.Float(string='Upon Drafting Agreement/Contract',copy=False)
    u21 = fields.Float(string='Vetting Charges',copy=False)
    u22 = fields.Float(string='Upon submitting final TSR',copy=False)
    u23 = fields.Float(string='Upon disposal of Interim application',copy=False)
    u24 = fields.Float(string='Advance billing',copy=False)
    u25 = fields.Float(string='Upon completion ',copy=False)
    u26 = fields.Float(string='Upon commencement of work',copy=False)
    u27 = fields.Float(string='Upon Drafting',copy=False)
    uion = fields.Float(string='Upon Issuance of Notice',copy=False)
    clerkage = fields.Float(string='Clerkage',copy=False)
    psv = fields.Float(string='Police Station Visit',copy=False)
    rep = fields.Float(string='Retainership',copy=False)

#    @api.model
#    def default_get(self, fields):
#        res = super(CaseSheet, self).default_get(fields)
#        company_id = self.env['res.company'].browse(self.env.context.get('active_ids', False))
#        print("\n\n\n\n RES : ", res)
#        res.update({
#            'we_thank_you': company_id.we_thank_you,
#            'scope_of_work': company_id.scope_of_work,
#            'annexure_one': company_id.annexure_one,
#            'annexure_three': company_id.annexure_three,
#        })
#        print("\n\n\n\n company_id : ", res.get('company_id'))
#        # if res.get('company_id'):
#        #     res['scope_of_work'] = self.env['res.company'].browse(res['company_id']).scope_of_work
#        #     res['annexure_one'] = self.env['res.company'].browse(res['company_id']).annexure_one
#        #     res['annexure_three'] = self.env['res.company'].browse(res['company_id']).annexure_three
#        return res

#     _defaults = {
#     	'date':lambda *a: time.strftime('%Y-%m-%d'),
# #     	'lodging_date':lambda *a: time.strftime('%Y-%m-%d'),
#         'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
#     	'state':'new',
#     	'name': lambda obj, cr, uid, context: '/',
#         'active': True,
#     }

#     def _check_fixed_price_amount(self, cr, uid, ids, context=None):
#         for case_obj in self.browse(cr, uid, ids, context=context):
#             total_amount = 0.0
#             for line_obj in case_obj.stage_lines:
#                 total_amount += line_obj.amount + line_obj.out_of_pocket_amount
#             if total_amount > case_obj.fixed_price:
#                 return False
#         return True

    @api.multi
    def _check_fixed_price_amount(self):
        for case_obj in self:
            total_amount = 0.0
            if case_obj.show_billing and case_obj.fixed_price and case_obj.bill_type == 'fixed_price':
                if case_obj.stage_lines:
                    for line_obj in case_obj.stage_lines:
                        total_amount += line_obj.amount + line_obj.out_of_pocket_amount
                    if total_amount != case_obj.fixed_price:
                        return False
                else:
                    return False
        return True

    _constraints = [
        (_check_fixed_price_amount, '\nError!\n\nFixed price stages amount total do not exceed the fixed price amount / Please enter tasks details in fixed price stages', ['fixed_price', 'stage_lines'])
#         (_check_stage_lines, '\nError!\n\nFixed price stages amount total do not exceed the fixed price amount / Please enter tasks details in fixed price stages', ['fixed_price', 'stage_lines']),

    ]


    @api.multi
    def fields_view_get(self,view_id=None, view_type=False, toolbar=False, submenu=False):

        res = super(CaseSheet,self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        return res

    # @api.onchange('department_ids')
    # def onchange_department_ids(self):
    #     result={}
    #     for line in self:
    #         if line.department_ids:
    #             for department in line.department_ids:
    #                 result = {'assignee_id': [('id', 'in', [department.manager_id.id for department in line.department_ids])]}
    #         return {'domain': result}

    @api.multi
    def button_refresh(self):
        return True

    @api.multi
    def case_user_access(self):
        cr=self.cr
        cr.execute("select id,project_id from case_sheet;")
        case_ids = map(lambda x: x, cr.fetchall())
        length = len(case_ids)
        i=1
        for data in case_ids:
            if data[1]:
                cr.execute('select uid from project_user_rel where project_id=%s;',(data[1],))
                user_ids = map(lambda x: x[0], cr.fetchall())
                for user in user_ids:
                    cr.execute('insert into case_user_rel values (%s,%s);',(data[0],user))
            _logger.info('Processing %s/%s'%(i,length))
            i += 1
        return True

    @api.multi
    def update_user_access_in_case_sheet(self):
        dept_pool = self.env['hr.department']
        employee_pool = self.env['hr.employee']
        self.env.cr.execute("select id,project_id, division_id,client_service_manager_id,client_service_executive_id,assignee_id from case_sheet where state not in ('draft','done','cancel','transfer');")
        case_ids = map(lambda x: x, self.env.cr.fetchall())
        length = len(case_ids)
        i=1
        for data in case_ids:
            employee_ids = []
            employee_ids.append(data[3])
            employee_ids.append(data[4])
            employee_ids.append(data[5])

            self.env.cr.execute('select assign_to from case_tasks_line where case_id=%s;',(data[0],))
            employee_ids += map(lambda x: x[0], self.env.cr.fetchall())
            self.env.cr.execute('select assign_to_in_associate from associate_tasks_line where case_id=%s;',(data[0],))
            employee_ids += map(lambda x: x[0], self.env.cr.fetchall())
            self.env.cr.execute('select assign_to_in_client from client_tasks_line where case_id=%s;',(data[0],))
            employee_ids += map(lambda x: x[0], self.env.cr.fetchall())

            div_obj  = dept_pool.browse(data[2])
            if div_obj.employee_ids:
                employee_ids += [emp.id for emp in div_obj.employee_ids]
            if div_obj.manager_id:
                employee_ids.append(div_obj.manager_id.id)
            parent_ids = dept_pool.get_parent_records(div_obj, [])
            for dep_obj in parent_ids:
                if dep_obj.manager_id:
                    employee_ids.append(dep_obj.manager_id.id)

            employee_ids=list(set(employee_ids))
            if None in employee_ids:
                employee_ids.remove(None)
            if False in employee_ids:
                employee_ids.remove(False)
            self.env.cr.execute('delete from project_user_rel where project_id=%s;',(data[1],))
            self.env.cr.execute('select id from hr_employee where id in %s;',(tuple(employee_ids),))
            employee_ids = map(lambda x: x[0], self.env.cr.fetchall())
            user_ids = [emp.user_id.id for emp in employee_pool.browse(employee_ids) if emp and emp.user_id]
            user_ids = list(set(user_ids))
            if data[1]:
                for user in user_ids:
                    self.env.cr.execute('insert into project_user_rel values (%s,%s);',(data[1],user))
            _logger.info('Processing %s/%s'%(i,length))
            i += 1

        return True

    @api.multi
    def update_tasks_date(self):

        self.env.cr.execute('select id,start_date,task_id,(select state from project_task as pt where ct.task_id=id) from case_tasks_line as ct where ct.days=0;')
        lines = map(lambda x: x, self.env.cr.fetchall())
        self.env.cr.execute('select id,start_date,task_id,(select state from project_task as pt where at.task_id=id) from associate_tasks_line as at where at.days=0;')
        lines += map(lambda x: x, self.env.cr.fetchall())
        self.env.cr.execute('select id,start_date,task_id,(select state from project_task as pt where cl.task_id=id) from client_tasks_line as cl where cl.days=0;')
        lines += map(lambda x: x, self.env.cr.fetchall())

        for data in lines:
            if data[3] != 'done':
                return_date = (datetime.strptime(data[1], '%Y-%m-%d') + timedelta(days=730)).strftime('%Y-%m-%d')
                return_date = self.env['hr.holidays.public'].get_next_working_day(return_date)
                ret = str(return_date.strftime('%Y-%m-%d'))
                self.env.cr.execute('update case_tasks_line set planned_completion_date=%s,days=%s where id=%s;',(ret, 730, data[0]))
                self.env.cr.execute('update project_task set date_deadline=%s,planned_hours=%s,date_end=%s where id=%s;',(ret, 730*8, return_date, data[2]))

        return True

    @api.multi
    def get_selection_value(self, field, field_id):
        res = ''
        if not field_id:
            return res
        fields_get_result = self.fields_get([field,])
        if fields_get_result:
            selection = fields_get_result[field]['selection']
            if selection:
                for key_value in selection:
                    if field_id == key_value[0]:
                        res = key_value[1]
        return res

    @api.multi
    def read(self, fields=None,load='_classic_read'):
        if self._context is None:
            context = {}
        res = super(CaseSheet, self).read(fields=fields, load=load)
        if self._context.get('exported', False) and res and self.ids:
            type = False
            if isinstance(self.ids, int):
                type = res['work_type']
            elif isinstance(self.ids, list):
                type = res[0]['work_type']
            if type:
                work_type = self.get_selection_value('work_type' , type).encode('utf8', 'ignore')
                if isinstance(self.ids, int):
                    res['work_type'] = work_type
                elif isinstance(self.ids, list):
                    res[0]['work_type'] = work_type
        return res


    #Starting // Automatically load work_type using division_id // Sanal Davis // 5-6-15
    @api.onchange('division_id')
    def onchange_division_id(self):
        work_type = False
        if self.division_id:
            department = self.env['hr.department'].browse(self.division_id.id)
            work_type = (department.work_type or False)
        return {'value': {'work_type' : work_type}}

    #Load Client Relationship Manager using Client Service Executive
    # @api.onchange('client_service_executive_id')
    # def onchange_service_manager(self):
    #     client_service_manager_id = False
    #     if self.client_service_executive_id:
    #         employee = self.env['hr.employee'].browse(self.client_service_executive_id.id)
    #         client_service_manager_id = (employee.parent_id and employee.parent_id.id or False)
    #     return {'value': {'client_service_manager_id' : client_service_manager_id}}

    # Set District As Null when Change the State
    @api.onchange('state_id')
    def onchange_state(self):
        self.district_id = False

    @api.multi
    def update_assignment_hours(self):
        if not self._context:
            context = {}
        for case in self:
            for line in case.assignment_hourly_lines:
                if line.hours_spent>0:
                    remaining_hours = line.remaining_hours + line.hours_spent
                    line.write({'remaining_hours':remaining_hours,'hours_spent':0})
        return True

    @api.model
    def default_get(self,fields_list):
        global line_count_slno
        line_count_slno = 0
        res = super(CaseSheet, self).default_get(fields_list)
        company_id = self.env.user.company_id
        #xprint("\n\n\n\n RES : ", res)
        res.update({
            'we_thank_you': company_id.we_thank_you,
            'scope_of_work': company_id.scope_of_work,
            'annexure_one': company_id.annexure_one,
            'annexure_three': company_id.annexure_three,
        })
        return res

    @api.onchange('bill_type', 'casetype_id')
    def onchange_bill_type(self):
        val = {}
        for case in self:
            if case.bill_type and not case.casetype_id:
                warning = {
                   'title': _('Error!'),
                   'message' : _('Please select Case Type first before selecting the Billing Type')
                }
                val['bill_type'] = False
                return {'value': val, 'warning': warning}
            elif case.bill_type == 'fixed_price':
                fixed_price =case.casetype_id.prefixed_price
                val = {'fixed_price':fixed_price, 'hearing_type': 'lumpsum'}
            else:
                val = {'hearing_type': 'hearing_limit'}
            # if case.bill_type == 'fixed_price':
            #     self.hearing_type = 'lumpsum'
            return {'value':val}

    @api.onchange('client_id', 'our_client')
    def onchange_client(self):
        val = {'first_parties' : [], 'opp_parties': []}
        if self.client_id:
            client = self.env['res.partner'].browse(self.client_id.id)
            if self.our_client == 'first':
                val['first_parties'] = [(0, 0, {'type':'claimaints','name':client.name,})]
            else:
                val['opp_parties'] = [(0, 0, {'type':'respondant', 'name':client.name,})]
            val['client_service_manager_id'] = client.client_manager_id and client.client_manager_id.id or False
        return {'value':val}

    @api.onchange('our_client','client_id')
    def onchange_our_client(self):
        val = {'first_parties' : [], 'opp_parties': []}
        if self.client_id and self.our_client:
            client = self.env['res.partner'].browse(self.client_id.id)
            if self.our_client == 'first':
                val['first_parties'] = [(0, 0, {'type':'claimaints','name':client.name,})]
            else:
                val['opp_parties'] = [(0, 0, {'type':'respondant', 'name':client.name,})]
        return {'value':val}


#    @api.onchange('recep_date','count','target_field')
#    def onchange_cnt(self):
#        return_date = (datetime.strptime(self.recep_date, '%Y-%m-%d') + timedelta(days=self.count)).strftime('%Y-%m-%d')
#        val = {
#            self.target_field: str(return_date)
#        }
#        return {'value': val}

    @api.onchange('ho_branch_id')
    def onchange_ho_branch_id(self):
        for case in self:
            if case.ho_branch_id:
                case.client_service_executive_id = case.ho_branch_id.client_service_executive_id.id

        #unuse code
#        val = {
#            'division_id': False,
#            'assignee_id': False,
#            }
#         if ho_branch:
#             obj = self.pool.get('ho.branch').browse(cr, uid, ho_branch)
#             state_id = obj.state_id.id
#             val = {
#                 'state_id': state_id
#             }
#         else:
#             val = {'state_id':False}
#        return {'value': val}

   #on button
    @api.multi
    def hold_case_sheet(self):
        for case_obj in self:
            type_ids = self.env['project.task.type'].search([('state', '=', 'hold')])
            if type_ids:
                self.env.cr.execute("update project_task set state='hold', stage_id=%s  where project_id=%s and state in ('draft','pending', 'open');",(type_ids[0].id, case_obj.project_id.id))
        return self.write({'state': 'hold'})

#on button
    @api.multi
    def reopen_case_sheet(self):
        for obj in self:
            if obj.project_id:
                # self.write([obj.id], {'state':'inprogress'})
                # obj.write({'state':'inprogress'})
                obj.write({
                    'state':'inprogress',
                    'close_date': False,
                    'close_comments': False,
                    'closure_type': False,
                    'time_duration': False,
                    'approve_closure_date': False
                })
                type_ids = self.env['project.task.type'].search([('state', '=', 'open')])
                if type_ids:
                    self.env.cr.execute("update project_task set state='open', stage_id=%s  where project_id=%s and state in ('hold');",(type_ids[0].id, obj.project_id.id))
            else:
                # self.write([obj.id], {'state':'new'})
                obj.write({'state':'new'})
        return True

    # submit casesheet for approval
    @api.multi
    def submit_for_approval_casesheet(self):
        # Send mail for create case sheet
        group = self.env['res.groups'].search([('name', '=', 'Client Service Executive')])
        if group:
            user_ids = self.env['res.users'].sudo().search([('groups_id', 'in', [group.id])])
            email_to = ''.join([user.partner_id.email + ',' for user in user_ids])
            email_to = email_to[:-1]
        else:
            email_to = self.user_id.partner_id.email
        ctx = dict(self.env.context or {})
        # sale_id = self.env['sale.order'].browse(self.id)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        fragment = {
            'model': 'case.sheet',
            'view_type': 'form',
            'id': self.id,
        }
        url = urllib.parse.urljoin(base_url,
                                   "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_for_case_sheet_request', raise_if_not_found=False)
        ctx.update({
            'casesheet_id': self.name,
            'url_link': url,
            'email_to': email_to,
        })
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
        return self.write({'state': 'waiting'})

    # Resubmit casesheet for approval
    @api.multi
    def resubmit_for_approval_casesheet(self):
        self.submit_for_approval_casesheet()

    @api.multi
    def confirm_casesheet(self):
        casesheet = self
        casesheet_name = casesheet.name or ''
        date_today = time.strftime('%Y-%m-%d')
        if casesheet.name == '/':
            branch = casesheet.ho_branch_id
            seqid = False
            if not branch.sequence_id:
                seqid = self.env['ho.branch'].create_sequence({'name':branch.name})
                branch.write({'sequence_id':seqid.id})
            # new_seq = self.env['ir.sequence'].next_by_code('case.sheet')
            new_seq = self.env['ir.sequence'].browse(seqid and seqid or branch.sequence_id.id).next_by_id()
            casesheet_name = branch.code+'/'+ casesheet.client_id.client_data_id + new_seq or '/'
            self.write({'name': casesheet_name, 'date': date_today})

        type_ids = []
        task_type_pool = self.env['project.task.type']
        project_pool = self.env['project.project']
        task_pool = self.env['project.task']
        dept_pool = self.env['hr.department']
        user_pool = self.env['res.users']
        csm = user_pool.has_group('legal_e.group_legal_e_client_service_manager')
        if csm:
            csm_super_id = SUPERUSER_ID
        analy_ids = task_type_pool.search([('name','=','New')])
        if len(analy_ids)>0:
            type_ids.append(analy_ids[0].id)
        else:
            analy_id = task_type_pool.create({'name':'New','state':'draft','sequence':1})
            type_ids.append(analy_id.id)
        work_ids = task_type_pool.search([('name','=','In Progress')])
        if len(work_ids)>0:
            type_ids.append(work_ids[0].id)
        else:
            work_id = task_type_pool.create({'name':'In Progress','state':'open','sequence':2})
            type_ids.append(work_id.id)

        hold_ids = task_type_pool.search([('name','=','Hold')])
        if len(hold_ids)>0:
            type_ids.append(hold_ids[0].id)
        else:
            hold_id = task_type_pool.create({'name':'Hold','state':'pending','sequence':3})
            type_ids.append(hold_id.id)

        pending_ids = task_type_pool.search([('name','=','Pending')])
        if len(pending_ids)>0:
            type_ids.append(pending_ids[0].id)
        else:
            pending_id = task_type_pool.create({'name':'Pending','state':'pending','sequence':5})
            type_ids.append(pending_id.id)

        done_ids = task_type_pool.search([('name','=','Completed')])
        if len(done_ids)>0:
            type_ids.append(done_ids[0].id)
        else:
            done_id = task_type_pool.create({'name':'Completed','state':'done','sequence':4})
            type_ids.append(done_id.id)
        tot = 0.0
        for bill in casesheet.stage_lines:
            tot += bill.amount + bill.out_of_pocket_amount

        if tot != casesheet.fixed_price:
            raise UserError(_('Fixed price amount must be equal to the billing stage line total amount .'))

        members = []
        if casesheet.client_service_executive_id:
            members.append(casesheet.client_service_executive_id.user_id.id)
        if casesheet.client_service_manager_id:
            members.append(casesheet.client_service_manager_id.user_id.id)
        if casesheet.division_id.employee_ids:
            if casesheet.division_id.manager_id:
                members.append(casesheet.division_id.manager_id.user_id.id)
            for empl in casesheet.division_id.employee_ids:
                if empl.user_id:
                    members.append(empl.user_id.id)
        parent_ids = dept_pool.get_parent_records(casesheet.division_id, [])
        for dep_obj in dept_pool.browse(parent_ids):
            if dep_obj.manager_id:
                members.append(dep_obj.manager_id.user_id.id)
        members = list(set(members))
        #Create a New Project
        if not casesheet.project_id:
            project_id = project_pool.create({'name':casesheet_name,'allow_timesheets':True,'privacy_visibility':'employees','partner_id':casesheet.client_id.id,'user_id':casesheet.assignee_id.user_id.id,'case_id': casesheet.id,'type_ids': [(6, 0, type_ids)],'members':[(6, 0, members)] or False})
        else:
            project_id = casesheet.project_id
            try:
                project_id.write({'name':casesheet_name,'user_id':casesheet.assignee_id.user_id.id, 'members':[(6, 0, members)]})
            except Exception:
                project_id.write({'name':casesheet_name,'members':[(6, 0, members)]})
                casesheet.project_id.analytic_account_id.write({'user_id':casesheet.assignee_id.user_id.id})

        if members:
            self.write({'members':[(6, 0, members)] or False})
        # Create Assignee Project Phases & Tasks
        i = 0
        for line in casesheet.tasks_lines:
            if not line.task_id:
                assigned = self.env['hr.employee'].browse(line.assign_to.id)
                if not assigned.user_id.id in project_id.members.ids:
                    project_id.write({'members':[(4,assigned.user_id.id)] or False})
                    self.write({'members':[(4, assigned.user_id.id)]})

                task_vals = {'project_id':project_id.id,'lot_name': casesheet.lot_name, 'name':line.name.id,'task_for':'employee','date_deadline':line.planned_completion_date,'assignee_id':line.assign_to  and line.assign_to.id or casesheet.assignee_id.id, 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8,'remaining_hours':line.days*8}
                if i == 0:
                    task_type_ids = self.env['project.task.type'].search([('state', '=', 'open')],order='sequence',limit=1)
                    task_vals.update({'state': 'open', 'stage_id': task_type_ids.id})
                    i += 1
                task_id = task_pool.create(task_vals)

                if line.start_date == date_today:
                    line.write({'task_id': task_id.id})
                else:
                    return_date = (datetime.strptime(date_today, '%Y-%m-%d') + timedelta(days=line.days)).strftime('%Y-%m-%d')
                    return_date = str(self.env['hr.holidays.public'].get_next_working_day(return_date))
                    line.write({'task_id':task_id.id, 'start_date': date_today, 'planned_completion_date': return_date})
        # Create Associate Project Phases & Tasks
        for line in casesheet.associate_tasks_lines:
            if not line.task_id :
                task_id = task_pool.create({'project_id':project_id.id,'lot_name': casesheet.lot_name,'name':line.name.id,'task_for':'associate','date_deadline':line.planned_completion_date,'other_assignee_id':(line.assign_to_in_associate.id and line.assign_to_in_associate.id or (casesheet.other_assignee_id.id and casesheet.other_assignee_id.id or False)), 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8,'remaining_hours':line.days*8})
                if line.start_date == date_today:
                   line.write({'task_id':task_id.id})
                else:
                    return_date = (datetime.strptime(date_today, '%Y-%m-%d') + timedelta(days=line.days)).strftime('%Y-%m-%d')
                    return_date = str(self.env['hr.holidays.public'].get_next_working_day(return_date))
                    line.write({'task_id':task_id, 'start_date': date_today, 'planned_completion_date': return_date})

        # Create Client Project Phases & Tasks
        # COMMENT THIS CODE BECAUSE DONT WANT TO CREATE PROJECT TASK
        # for line in casesheet.client_tasks_lines:
        #     if not line.task_id:
        #         task_id = task_pool.create({'project_id':project_id.id,'lot_name': casesheet.lot_name,'name':line.name.id,'task_for':'customer','date_deadline':line.planned_completion_date,'client_id':line.assign_to_in_client.id and line.assign_to_in_client.id or casesheet.client_id.id, 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8,'remaining_hours':line.days*8})
        #         if line.start_date == date_today:
        #             line.write({'task_id':task_id.id})
        #         else:
        #             return_date = (datetime.strptime(date_today, '%Y-%m-%d') + timedelta(days=line.days)).strftime('%Y-%m-%d')
        #             return_date = str(self.env['hr.holidays.public'].get_next_working_day(return_date))
        #             line.write({'task_id':task_id.id, 'start_date': date_today, 'planned_completion_date': return_date})

        # Send mail to CSM heads
        if not casesheet.client_service_executive_id:
            raise UserError(_('Enter Client Service Manager!'))
        if not casesheet.client_service_manager_id:
            raise UserError(_('Enter Client Relationship Manager!'))
        if not casesheet.assignee_id:
            raise UserError(_('Enter Assignee!'))
        email_to = ''.join([casesheet.client_service_executive_id.work_email + ',' +
                            casesheet.client_service_manager_id.work_email + ',' + casesheet.assignee_id.work_email])
        ctx = dict(self.env.context or {})
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        fragment = {
            'model': 'case.sheet',
            'view_type': 'form',
            'id': casesheet.id,
        }
        url = urllib.parse.urljoin(base_url,
                                   "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_for_case_sheet_confirm_request',
                                   raise_if_not_found=False)
        ctx.update({
            'casesheet_id': casesheet.name,
            'url_link': url,
            'email_to': email_to,
        })
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
        return self.write({'state':'inprogress', 'project_id': project_id.id})

    @api.multi
    def reject_casesheet(self):
        try:
            view_id = self.env.ref('legal_e.wizard_reject_case_sheet').id
        except ValueError as e:
            view_id = False
        return {
            'name': "Reject Case Sheet",
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'res_model': 'reject.case.sheet',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'casesheet_id': self.id
            }
        }

    @api.multi
    def write(self, vals):
        res = super(CaseSheet, self).write(vals)
        if vals.get('fixed_price', False):
            for case_obj in self:
                if case_obj.state != 'new':
                    if not self.env['res.users'].has_group('legal_e.group_case_sheet_operation_manager'):
                        raise UserError(_('Warning!'), _('You are not permitted to modifie the Fixed Price Amount.Please contact case sheet operations manager.'))

        return res

    @api.model
    def create(self, vals):
        if self._context is None:
            context = {}
        employee_obj = self.env['res.partner'].browse(vals['client_id'])
        if not vals.get('contact_partner1_id', False):
            if employee_obj.child_ids:
                for item in employee_obj.child_ids:
                    vals['contact_partner1_id'] = item.id
                    break
        if not vals.get('court_proceedings',False)==[] and 'tasks_lines' in vals and len(vals['tasks_lines'])<=0:
            raise UserError(_('Please enter the Assignee Tasks Details.'))
        vals.update({'show_billing': True})
        vals.update({'name':'/'})
#         if vals.get('division_id', False) and vals.get('assignee_id', False):
#             department = self.pool.get('hr.department').browse(cr, uid, vals['division_id'], context=context)
#             if department.manager_id.id != vals['assignee_id']:
#                 raise openerp.exceptions.Warning(_('Please enter the department head as assignee in casesheet.'))

        res = super(CaseSheet, self).create(vals)
        if self._context.get('case_copy', False):
            case_obj = res
            for line in case_obj.tasks_lines:
                for bill in case_obj.stage_lines:
                    if bill.name.id == line.name.id:
                        # self.env['fixed.price.stages'].write([bill.id], {'name': line.id})
                        bill.write({'name': line.id})
        return res

    @api.multi
    def update_casesheet(self):
        case_ids = self.search([('lot_name','=', 'NS13')])
        for case_obj in case_ids:
            for line in case_obj.tasks_lines:
                for bill in case_obj.stage_lines:
                    if bill.name.name == line.name:
                        bill.write({'name': line.id})
        return True

    @api.multi
    def update_project(self):
        project_ids = self.env['project.project'].search([('name', '=', '/')])
        for project_id in project_ids:
            case_ids = self.search([('project_id','=', project_id)])
            for case_obj in case_ids:
                project_id.write({'name': case_obj.name})
        return True

    @api.multi
    def copy(self,default=None):
        context=self.env.context.copy() or {}
        context.update({'case_copy': True})
        default = default or {}
        default.update({
            'state':'new',
            'name':'/',
            'date':time.strftime('%Y-%m-%d'),
            'project_id':False,
            'court_proceedings': [],
            'inward_register': [],
            'outward_register': [],
            'assignment_history': [],
            'show_billing': False,
            'active': True,
        })

        # if not self._context.get('bulk_case', False):
        #     default.update({
        #         'lot_name': False,
        #         'client_service_manager_id': False,
        #         'client_service_executive_id': False,
        #         'assignee_id': False,
        #         'tasks_lines': []
        #     })
        retval = super(CaseSheet, self).copy(default)
        return retval

    def unlink(self):
        if self._context is None:
            context = {}
#         unlink_ids = []
#         raise openerp.exceptions.Warning(_('You cannot delete a Case Sheet.'))
#         osv.osv.unlink(self, cr, uid, unlink_ids, context=context)

        for case_obj in self:
            if case_obj.project_id:
                task_ids = self.env['project.task'].search([('project_id', '=', case_obj.project_id.id)])
                if task_ids:
                    self.env['project.task'].unlink()
                case_obj.project_id.unlink()

        res = super(CaseSheet, self).unlink()
        return res

    @api.multi
    def view_court_proceedings(self):
        view_id = self.env.ref('legal_e.court_proceedings_tree').id
        proceed_ids = []
        for case_obj in self:
            proceed_ids += [proceed.id for proceed in case_obj.court_proceedings]
        #choose the view_mode accordingly
        if proceed_ids:
            domain=[('id','in',proceed_ids)]
            return{
                'name':'Court Proceedings',
                'type': 'ir.actions.act_window',
                'res_model': 'court.proceedings',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': view_id,
                'views': [(self.env.ref('legal_e.court_proceedings_tree').id, 'tree'),
                          (self.env.ref('legal_e.court_proceedings_form').id, 'form')],
                'domain': domain
            }
        else:
            res = self.env['ir.model.data'].get_object_reference('legal_e', 'court_proceedings_form')
            view=res and res[1] or False
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view,
                'res_model': 'court.proceedings',
                'type': 'ir.actions.act_window',
                'context':{'default_case_id': self.ids[0],},
                'res_id':False
            }

    @api.multi
    def view_man_hours(self):
        view_id = self.env.ref('legal_e.man_hours_tree').id
        return {
            'name': 'Man Hours',
            'type': 'ir.actions.act_window',
            'res_model': 'man.hours',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': view_id,
            'views': [(view_id, 'tree')],
            'domain': [('case_id', 'in', self.ids)],
        }

    # @api.multi
    # def view_court_proceedings(self):
    #     mod_obj = self.env['ir.model.data']
    #     act_obj = self.env['ir.actions.act_window']
    #
    #     result = mod_obj.get_object_reference('legal_e', 'action_court_proceedings')
    #     view_id = result and result[1] or False
    #     result = act_obj.read([id])
    #     # result = act_obj.read([id])[0]
    #     proceed_ids = []
    #     for case_obj in self:
    #         proceed_ids += [proceed.id for proceed in case_obj.court_proceedings]
    #     #choose the view_mode accordingly
    #     if proceed_ids:
    #         result['domain'] = "[('id','in',["+','.join(map(str, proceed_ids))+"])]"
    #     else:
    #         res = mod_obj.get_object_reference('legal_e', 'court_proceedings_form')
    #         result['views'] = [(res[1] or False, 'form')]
    #         # result['views'] = [(res and res[1] or False, 'form')]
    #         result['res_id'] = False
    #         result['context'] = {
    #             'default_case_id': self.ids[0],
    #             }
    #     return result

    # @api.multi
    # def project_tree_view(self):
    #     obj = self
    #     mod_obj = self.env['ir.model.data']
    #     act_obj = self.env['ir.actions.act_window']
    #     result = mod_obj.get_object_reference('project', 'act_project_project_2_project_task_all')
    #     id = result and result[1] or False
    #     result = act_obj.read([id])
    #     # result = act_obj.read([id])[0]
    #     result['context'] = {
    #         'search_default_project_id': [obj.project_id.id],
    #         'default_project_id': obj.project_id.id,
    #         'active_test': False
    #         }
    #     return result

    @api.multi
    def project_tree_view(self):
        obj = self
        view_id = self.env.ref('project.act_project_project_2_project_task_all').read()[0]
        ctx={
            'search_default_project_id': obj.project_id.id,
            'default_project_id': obj.project_id.id,
            'active_test': False
        }
        return {
           'name': _('Project'),
           'type': 'ir.actions.act_window',
           'res_model': 'project.task',
           'view_id': view_id,
           'view_mode':'kanban'

        }

    @api.onchange('client_id')
    def onchange_client_id(self):
        if self.client_id:
            self.client_service_manager_id = self.client_id.client_manager_id.id
            addr = self.env['res.partner'].search([('parent_id', '=', self.client_id.id), ('type', '=', 'contact')])
            val = {
                'contact_partner1_id': (addr and len(addr) > 0 and addr[0] or False),
                'contact_partner2_id': (addr and len(addr) > 1 and addr[1] or False),
            }
            if self.client_id.referral_specification == 'client_specific':
                self.referral_specification = self.client_id.referral_specification
                self.referral_type = self.client_id.referral_type
                if self.client_id.referral_type and self.client_id.referral_type=='ref_emp':
                    self.response_person_emp = self.client_id.response_person_emp
                if self.client_id.referral_type and self.client_id.referral_type=='ref_part':
                    self.response_person_emp = self.client_id.assignee_id
                self.referral_ref = self.client_id.ref
                self.referral_percentage = self.client_id.referral_percentage
                self.referral_amount = self.client_id.referral_amount
                self.referral_validity = self.client_id.referral_validity
            else:
                self.referral_specification = self.client_id.referral_specification
                self.referral_type = False
                self.response_person_emp = False
                self.response_person = False
                self.referral_ref = False
                self.referral_percentage = False
                self.referral_amount = False
                self.referral_validity = False
            return {'value': val}
        else:
            return {'value': {'contact_partner1_id': False, 'contact_partner2_id': False}}

    @api.onchange('referral_specification')
    def onchange_referral_specification(self):
        if self.client_id.referral_specification == 'client_specific':
            self.referral_specification = self.client_id.referral_specification
            self.referral_type = self.client_id.referral_type
            if self.client_id.referral_type and self.client_id.referral_type=='ref_part':
                
                self.response_person_emp = self.client_id.assignee_id
            if self.client_id.referral_type and self.client_id.referral_type=='ref_emp':
                
                self.response_person_emp = self.client_id.response_person_emp
            self.referral_ref = self.client_id.ref
            self.referral_percentage = self.client_id.referral_percentage
            self.referral_amount = self.client_id.referral_amount
            self.referral_validity = self.client_id.referral_validity
        else:
            self.referral_type = False
            self.response_person = False
            self.response_person_emp = False
            self.referral_ref = False
            self.referral_percentage = False
            self.referral_amount = False
            self.referral_validity = False

    @api.onchange('work_type')
    def onchange_work_type(self):
        company_id = self.env.user.company_id
        if self.work_type == 'non_litigation':
            self.we_thank_you = company_id.nl_we_thank_you
            self.scope_of_work = company_id.nl_scope_of_work
            self.annexure_one = company_id.nl_annexure_one
            self.annexure_three = company_id.nl_annexure_three
        else:
            self.we_thank_you = company_id.we_thank_you
            self.scope_of_work = company_id.scope_of_work
            self.annexure_one = company_id.annexure_one
            self.annexure_three = company_id.annexure_three
        if not self.work_type:
        #     return {'value': {'casetype_id': False, 'fees_lines': False}}
        # return {'value': {'casetype_id': False, 'fees_lines': False}}
            return {'value': {'casetype_id': False}}
        return {'value': {'casetype_id': False}}


    @api.onchange('casetype_id')
    def onchange_case_type(self):
        if not self.casetype_id:
            return {'value': {'no_court':False}}
        no_court = self.env['case.master'].browse(self.casetype_id.id).no_court
        return {'value': {'no_court': no_court}}

    # create task template in case sheet task line
    @api.multi
    def save_tasks_as_template(self):
        obj = self
        tasksids = self.env['case.tasks.line'].search([('case_id','=',self.id)])
        for task in tasksids:
            self.env['task.template'].create({'name':obj.work_type,'casetype_id':obj.casetype_id.id, 'tasks_lines':[(0, 0, {'name':task.name.id,'slno':task.slno,'days':task.days})]})
        return True

    @api.multi
    def close_case_sheet(self):
        try:
            # view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'wizard_case_close_id')
            view_id = self.env.ref('legal_e.wizard_case_close_id').id
        except ValueError as e:
            view_id = False
        return {
            'name':_("Close Case"),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'res_model': 'case.close',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'case_id': self.ids
            }
        }

    @api.multi
    def approve_close_case_sheet_assignee(self):
        case_id = self.env['case.sheet'].browse(self.id)
        group_id = self.env.ref('account.group_account_user').id
        group = self.env['res.groups'].search([('id', '=', group_id)])
        if group:
            user_ids = self.env['res.users'].sudo().search([('groups_id', 'in', [group.id])])
            email_to = ''.join([user.partner_id.email + ',' for user in user_ids])
            email_to = email_to[:-1]
        else:
            email_to = self.user_id.partner_id.email
        ctx = dict(self.env.context or {})
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        fragment = {
            'model': 'case.sheet',
            'view_type': 'form',
            'id': case_id.id,
        }
        url = urllib.parse.urljoin(base_url,
                                   "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_for_case_closure_request_account', raise_if_not_found=False)
        ctx.update({
            'case_id': case_id.name,
            'url_link': url,
            'email_to': email_to,
        })
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
        case_id.write({'state': 'waiting_accounts'})

    @api.multi
    def reject_close_case_sheet_assignee(self):
        for obj in self:
            obj.write({
                'close_date': False,
                'close_comments': False,
                'closure_type': False,
                'time_duration': False,
            })
        view_id = self.env.ref('legal_e.wizard_reject_case_closure_assignee').id or False
        return {
            'name':_("Reject Case Closure Assignee"),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'res_model': 'reject.case.closure.assignee',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'case_id': self.id
            }
        }
    @api.multi
    def approve_close_case_sheet_accounts(self):
        case_id = self.env['case.sheet'].browse(self.id)
        group_id = self.env.ref('legal_e.group_case_closure_approval').id
        group = self.env['res.groups'].search([('id', '=', group_id)])
        if group:
            user_ids = self.env['res.users'].sudo().search([('groups_id', 'in', [group.id])])
            email_to = ''.join([user.partner_id.email + ',' for user in user_ids])
            email_to = email_to[:-1]
        else:
            email_to = self.user_id.partner_id.email
   
        user_id=self.env['res.users'].browse(1)
        email_to = user_id.partner_id.email
        ctx = dict(self.env.context or {})
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        fragment = {
            'model': 'case.sheet',
            'view_type': 'form',
            'id': case_id.id,
        }
        url = urllib.parse.urljoin(base_url,
                                   "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_for_case_closure_request_admin', raise_if_not_found=False)
        ctx.update({
            'case_id': case_id.name,
            'url_link': url,
            'email_to': email_to,
        })
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
        case_id.write({'state': 'waiting_admin'})

    @api.multi
    def approve_close_case_sheet_accounts1(self):
        case_id = self.env['case.sheet'].browse(self.id)
        if self._uid == case_id.assignee_id.user_id.id:
            raise UserError(_("Assignee Can't approve account part!"))
        type_ids = self.env['project.task.type'].search([('state', '=', 'done')], limit=1)
        if type_ids:
            self.env.cr.execute("update project_task set state='done', stage_id=%s  where project_id=%s;",
                                (type_ids.id, case_id.project_id.id))
        invoice_ids = self.env['account.invoice'].search([('case_id', '=', case_id.id)])
        for inv_obj in invoice_ids:
            if inv_obj.state not in ['paid', 'cancel']:
                raise UserError(_('Invoices related to this case sheet is not paid yet!'))
        case_id.write({'approve_closure_date': datetime.today().date(), 'state': 'done'})
        return True
    @api.multi
    def approve_close_case_sheet_admin(self):
        case_id = self.env['case.sheet'].browse(self.id)
        if self._uid == case_id.assignee_id.user_id.id:
            raise UserError(_("Assignee Can't approve account part!"))
        type_ids = self.env['project.task.type'].search([('state', '=', 'done')], limit=1)
        if type_ids:
            self.env.cr.execute("update project_task set state='done', stage_id=%s  where project_id=%s;",
                                (type_ids.id, case_id.project_id.id))
        invoice_ids = self.env['account.invoice'].search([('case_id', '=', case_id.id)])
        for inv_obj in invoice_ids:
            if inv_obj.state not in ['paid', 'cancel']:
                raise UserError(_('Invoices related to this case sheet is not paid yet!'))
        case_id.write({'approve_closure_date': datetime.today().date(), 'state': 'done'})
        return True

    @api.multi
    def reject_close_case_sheet_accounts(self):
        for obj in self:
            obj.write({
                'close_date': False,
                'close_comments': False,
                'closure_type': False,
                'time_duration': False,
            })
        view_id = self.env.ref('legal_e.wizard_reject_case_closure_accounts').id or False
        return {
            'name':_("Reject Case Closure Accounts"),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'res_model': 'reject.case.closure.accounts',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'case_id': self.id
            }
        }
    @api.multi
    def reject_close_case_sheet_admin(self):
        for obj in self:
            obj.write({
                'close_date': False,
                'close_comments': False,
                'closure_type': False,
                'time_duration': False,
            })
        view_id = self.env.ref('legal_e.wizard_reject_case_closure_admin').id or False
        return {
            'name':_("Reject Case Closure Admin"),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'res_model': 'reject.case.closure.admin',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'case_id': self.id
            }
        }

    @api.multi
    def cancel_case_sheet(self):
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'wizard_case_cancel_id')
        except ValueError as e:
            view_id = False
        return {
            'name':_("Cancel Case Sheet"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'case.cancel',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
            'case_id': self.ids
            }
        }
        #return self.write(cr, uid, ids, {'state':'cancel'})

    @api.multi
    def transfer_case_sheet(self):
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'wizard_case_transfer_id')
        except ValueError as e:
            view_id = False
        return {
            'name':_("Transfer Case Sheet"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'case.transfer',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
            'case_id': self.ids
            }
        }

    @api.onchange('work_type', 'casetype_id','assignee_id','date')
    def onchange_assignee(self):
        val = {}
        if self.casetype_id:
            case = False
            if self.ids:
                case = self.env['case.sheet'].browse(self.ids[0])
            tempids = self.env['task.template'].search([('name', '=', self.work_type),('casetype_id', '=', self.casetype_id.id)])
            temp_list = []
            if not self.date:
                date = time.strftime('%Y-%m-%d')
            else:
                date = self.date
            for tempmain in tempids:
                for temp in tempmain.tasks_lines:
                    return_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=temp.days)).strftime('%Y-%m-%d')
                    return_date = self.env['hr.holidays.public'].get_next_working_day(return_date)
                    temp_list.append({'slno':temp.slno,'name':temp.name.id,'days':temp.days,'planned_completion_date':str(return_date),'phase_name':temp.phase_name.id,'start_date': date,'state':'New','assign_to':self.assignee_id})
            val['tasks_lines']= temp_list
            if case and case.project_id:
                val['project_id.user_id'] = case.assignee_id.user_id.id
                self.update_project_details(self.assignee_id, self.division_id)
        return {'value': val}

    @api.onchange('litigation_type')
    def onchange_litigation_type(self):
        val = {}
        if self.litigation_type:
            if not self.fees_lines:
                temp_list = []
                litigation_ids = self.env['litigation.nonlitigation.template'].search([('name', '=', 'litigation'), ('litigation_type', '=', self.litigation_type)])
                for litigation in litigation_ids:
                    for line in litigation.litigation_lines:
                        temp_list.append({'slno': line.slno, 'product_id': line.name.id})
                val['fees_lines'] = temp_list
            # else:
            #     val['fees_lines'] = False
        return {'value': val}

    @api.onchange('nonlitigation_type')
    def onchange_nonlitigation_type(self):
        val = {}
        if self.nonlitigation_type:
            if not self.fees_lines:
                temp_list = []
                nonlitigation_ids = self.env['litigation.nonlitigation.template'].search([('name', '=', 'non_litigation'), ('litigation_type', '=', self.nonlitigation_type)])
                for nonlitigation in nonlitigation_ids:
                    for line in nonlitigation.litigation_lines:
                        temp_list.append({'slno': line.slno, 'product_id': line.name.id})
                val['fees_lines'] = temp_list
            # else:
            #     val['fees_lines'] = False
        return {'value': val}

    @api.multi
    def update_project_details(self, assignee_id, division_id):
        if self.ids:
            case = self.env['case.sheet'].browse(self.ids[0])
            assignee = self.env['hr.employee'].browse(assignee_id)
            members = []
            if assignee and assignee.department_id:
                emplids = self.env['hr.employee'].search([('department_id','=',assignee.department_id.id)])
                for empl in emplids:
                    if empl.user_id:
                        members.append(empl.user_id.id)
                        self.env['project.project'].write([case.project_id.id], {'user_id':assignee.user_id.id, 'members':[(4, empl.user_id.id)]})
                        # self.write([case.id], {'members':[(4, empl.user_id.id)]})
                        case.write({'members':[(4, empl.user_id.id)]})
        return True

    @api.multi
    def invoice_case_sheet(self):
        case = self
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'wizard_case_sheet_inv_id')
        except ValueError as e:
            view_id = False
        res = {}
        res.update({'case_id':case.id})
        res.update({'name':"Invoice For "+case.name})
        res.update({'bill_type':case.bill_type})
        res.update({'department_ids': [(6, 0, case.department_ids.ids)]})
        subject = ''
        oppo = False
        first = False
        if case.work_type != 'non_litigation':
            if case.court_id:
                subject = case.court_id.name + (case.court_location_id and ', ' + case.court_location_id.name or '')
            if case.reg_number:
                subject += '\n'+'Case No. : '+case.reg_number
            for fp in case.first_parties:
                first = (first and first+', '+fp.name or '\n'+fp.name)


            if first:
                subject +=first
                oppo=False
                for op in case.opp_parties:
                    oppo = (oppo and oppo+', '+op.name or '\n \tV/S \n'+op.name)
        if oppo:
            subject +=oppo
        res.update({'subject':subject})
        valslist = []
        valid = False

        flg_fixed_fixed_price_stage = True
        flg_fixed_other_exp_billable = True
        flg_assign_hourly_stage = True
        flg_assign_fixed_price_stage = True
        flg_assign_other_exp_billable = True
        flg_assign_court_proceed_billable = True
        other_expenses = False

        if 'flg_fixed_fixed_price_stage' in self._context:
            flg_fixed_fixed_price_stage = self._context['flg_fixed_fixed_price_stage']
        if 'flg_fixed_other_exp_billable' in self._context:
            flg_fixed_other_exp_billable = self._context['flg_fixed_other_exp_billable']
        if 'flg_assign_hourly_stage' in self._context:
            flg_assign_hourly_stage = self._context['flg_assign_hourly_stage']
        if 'flg_assign_fixed_price_stage' in self._context:
            flg_assign_fixed_price_stage = self._context['flg_assign_fixed_price_stage']
        if 'flg_assign_other_exp_billable' in self._context:
            flg_assign_other_exp_billable = self._context['flg_assign_other_exp_billable']
        if 'flg_assign_court_proceed_billable' in self._context:
            flg_assign_court_proceed_billable = self._context['flg_assign_court_proceed_billable']

        if case.bill_type == 'fixed_price' and flg_fixed_other_exp_billable:
            other_expenses = True
        elif case.bill_type == 'assignment_wise' and flg_assign_other_exp_billable:
            other_expenses = True
        # Billing Type is Fixed Price
        if case.bill_type == 'fixed_price':
            if flg_fixed_fixed_price_stage:
                valslist = []

                for line in case.stage_lines:
                    fixed_price_exist_ids = self.env['case.sheet.invoice'].search([('invoice_lines_fixed.ref_id','=',line.id), ('invoice_id','!=',False)])
                    if not line.invoiced and line.state == 'Completed' and not len(fixed_price_exist_ids):
                        valid = True
                        valslist.append((0, 0, {'name':line.name.name.name,'amount':line.amount,'ref_id':line.id, 'out_of_pocket_amount':line.out_of_pocket_amount, 'office_id':line.office_id.id, 'department_id':line.department_id.id, 'description': line.description}))
                        #added office field in above statement # Sanal Davis # 27/5/15
                res.update({'invoice_lines_fixed':valslist})
        else:
                valslist = []
                if flg_assign_hourly_stage:
                    for line in case.assignment_hourly_lines:
                        already_added_hours = 0.00
                        assign_hour_exist_ids = self.env['case.sheet.invoice'].search([('invoice_lines_assignment_hourly.ref_id','=',line.id), ('invoice_id','!=',False)])
                        for assign_hour in assign_hour_exist_ids:
                            for lin in assign_hour.invoice_lines_assignment_hourly:
                                remain = lin.bill_hours
                                if not remain or remain<=0:
                                    remain = lin.amount/line.amount
                                    remain = remain or 0.00
                            already_added_hours += remain
                        if not line.invoiced and (line.remaining_hours - already_added_hours)>0:
                            valid = True
                            valslist.append((0, 0, {'name':line.description,'amount':(line.amount*line.remaining_hours), 'ref_id': line.id, 'bill_hours':line.remaining_hours,'office_id':line.office_id and line.office_id.id or False}))
                    res.update({'invoice_lines_assignment_hourly':valslist})
                if flg_assign_fixed_price_stage:
                    valslist = []
                    for line in case.assignment_fixed_lines:
                        assign_fixed_exist_ids = self.env['case.sheet.invoice'].search([('invoice_lines_assignment_fixed.ref_id','=',line.id), ('invoice_id','!=',False)])
                        if not line.invoiced and line.state == 'Completed' and not len(assign_fixed_exist_ids):
                            valslist.append((0, 0, {'name':line.name.name.name,'amount':line.amount,'ref_id':line.id, 'out_of_pocket_amount':line.out_of_pocket_amount,'office_id':line.office_id and line.office_id.id or False}))
                            valid = True

                    res.update({'invoice_lines_assignment_fixed':valslist})

                # Court Proceedings
                if flg_assign_court_proceed_billable:
                    valslist = []
                    for line in case.court_proceedings:
                        court_exist_ids = self.env['case.sheet.invoice'].search([('invoice_lines_court_proceedings_assignment.ref_id','=',line.id), ('invoice_id','!=',False)])
                        if not line.invoiced and line.billable == 'bill' and not len(court_exist_ids):
                            valid = True
                            valslist.append((0, 0, {'effective':line.effective,'name':line.name,'amount':line.effective == 'effective' and case.effective_court_proceed_amount or case.non_effective_court_proceed_amount, 'date':line.proceed_date, 'ref_id': line.id, 'office_id':case.ho_branch_id.id}))
                    res.update({'invoice_lines_court_proceedings_assignment':valslist})
        #Other Expenses
        if other_expenses:
            valslist = []
            for line in case.other_expenses_lines:
                if line.expense_id and line.expense_type in ('adv_billing', 'associate_pay', 'petty_cash', 'third_party') and line.expense_id.state == 'draft':
                    raise ValidationError(_('Please approve expense for %s' % line.name))
                # if line.expense_id.sheet_id and line.expense_type in ('adv_billing', 'associate_pay', 'petty_cash', 'third_party') and line.expense_id.sheet_id[0].state != 'approve':
                if line.expense_id.sheet_id and line.expense_type in ('adv_billing', 'associate_pay', 'petty_cash', 'third_party') and line.expense_id.sheet_id[0].state in ['draft', 'submit']:
                    raise ValidationError(_('Please approve expense for %s') % (line.name))
                other_expense_exist_ids = self.env['case.sheet.invoice'].search([('invoice_lines_other_expenses.ref_id','=',line.id), ('invoice_id','!=',False)])
                # if not line.invoiced and line.billable == 'bill' and not len(other_expense_exist_ids) and line.expense_type == 'other_cash' and line.paid_amount <= 0.00:
                #     valid = True
                #     valslist.append((0, 0, {'name': line.name, 'amount': line.req_amount, 'ref_id': line.id, 'office_id': case.ho_branch_id.id}))
                # if not line.invoiced and line.billable == 'bill' and not len(other_expense_exist_ids) and line.expense_type == 'adv_billing' and line.paid_amount <= 0.00:
                #     valid = True
                #     valslist.append((0, 0, {'name': line.name, 'amount': line.req_amount, 'ref_id': line.id, 'office_id': case.ho_branch_id.id}))
                # if not line.invoiced and line.billable == 'bill' and not len(other_expense_exist_ids) and line.paid_amount > 0.00 and line.amount == 0.00:
                #     valid = True
                #     valslist.append((0, 0, {'name': line.name, 'amount': line.paid_amount, 'ref_id': line.id, 'office_id': case.ho_branch_id.id}))
                #     # if line.date<='2019-03-16':
                #     #     valslist.append((0, 0, {'name':line.name,'amount':line.amount,'ref_id':line.id, 'office_id':case.ho_branch_id.id}))
                #     # else:
                #     #     valslist.append((0, 0, {'name':line.name,'amount':line.paid_amount,'ref_id':line.id, 'office_id':case.ho_branch_id.id}))
                # elif not line.invoiced and line.billable == 'bill' and not len(other_expense_exist_ids) and line.amount > 0.00 and line.paid_amount == 0.00 and line.req_amount == 0.00:
                #     valid = True
                #     valslist.append((0, 0, {'name': line.name, 'amount': line.amount, 'ref_id': line.id, 'office_id': case.ho_branch_id.id}))
                if not line.invoiced and line.billable == 'bill' and not len(other_expense_exist_ids) and line.req_amount > 0.00 and line.amount == 0.00:
                    valid = True
                    valslist.append((0, 0, {'name': line.name, 'amount': line.req_amount, 'ref_id': line.id, 'office_id': case.ho_branch_id.id}))
                elif not line.invoiced and line.billable == 'bill' and not len(other_expense_exist_ids) and line.amount > 0.00 and line.paid_amount == 0.00 and line.req_amount == 0.00:
                    valid = True
                    valslist.append((0, 0, {'name': line.name, 'amount': line.amount, 'ref_id': line.id, 'office_id': case.ho_branch_id.id}))

            res.update({'invoice_lines_other_expenses':valslist})
        if not valid and not 'consolidated_id' in self._context:
             raise UserError(_('Nothing to Invoice'))
        if 'consolidated_id' in self._context and self._context['consolidated_id']:
             res.update({'consolidated_id':self._context['consolidated_id']})
        invid = self.env['case.sheet.invoice'].create(res)
        return {
            'name':_("Invoice Case Sheet"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'case.sheet.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'res_id': invid.id,
            'valid': valid
            }

    @api.multi
    def view_related_invoices(self):
        invoices=self.env['case.sheet.invoice'].search([('case_id', 'in', self.ids), ('invoice_id', '!=', False)])
        return {
           'name': _('Customer Invoice'),
           'type': 'ir.actions.act_window',
           'res_model': 'account.invoice',
           'domain': [('case_id', 'in', self.ids), ('partner_id.associate', '=', False)],
           'view_id': self.env.ref('account.invoice_tree').id,
           'views':[(self.env.ref('account.invoice_tree').id,'tree'),(self.env.ref('account.invoice_form').id,'form')],
           # 'view_mode':'tree'
       }
#        obj = self.browse(self.ids[0])
#        sear = self.env['case.sheet.invoice'].search([('case_id','=',obj.id),('invoice_id','!=',False)])
#        try:
#            dummy, view_id = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
#        except ValueError as e:
#            view_id = False
#        lst = []
#        for dt in self.env['case.sheet.invoice'].read(sear,['invoice_id']):
#            lst.append(dt['invoice_id'][0])
#        return {
#                'name': _('Customer Invoice'),
#                'view_type': 'form',
#                "view_mode": 'tree, form',
#                'res_model': 'account.invoice',
#                'type': 'ir.actions.act_window',
#                # 'domain': "[('type','=','out_invoice')]",
#                'domain': "[('type','=','out_invoice'),('id','in',("+str(lst)+"))]",
#                'view_id': False,
#                'target':'current',
#                 'context':{'form_view_ref':'account.invoice_form'}
#        }

    @api.multi
    def view_casesheet_invoices(self):
        return {
            'name': _('Case Sheet Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'case.sheet.invoice',
            'view_id': self.env.ref('legal_e.case_sheet_inv_tree').id,
            'views': [(self.env.ref('legal_e.case_sheet_inv_tree').id, 'tree'),
                      (self.env.ref('legal_e.wizard_case_sheet_inv_id').id, 'form')],
            'domain': [('case_id', 'in', self.ids)],
        }

    @api.multi
    def view_related_expenses(self):
        # View related expenses from case sheet
        return {
            'name': _('Expense'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('hr_expense.view_expenses_tree').id,
            'views': [(self.env.ref('hr_expense.view_expenses_tree').id, 'tree'),
                      (self.env.ref('hr_expense.hr_expense_form_view').id, 'form')],
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id},
        }

    # Sanal Davis // 9-6-15
    @api.multi
    def view_related_petty_cash(self):
        '''
            View related petty cash from case sheet
        '''
        obj = self.browse(self.ids[0])
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'view_move_line_tree_legal_e_inherit')
        except ValueError as e:
            view_id = False
        return {
                'name': _('Summary'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'domain': "[('case_id','=',"+str(obj.id)+")]",
                'context': {'search_default_case_id':[obj.id], 'default_case_id': obj.id},
        }


class FeeInfoLine(models.Model):
    _name = 'fee.info.line'
    _order = 'slno asc'

    @api.depends('no_of_hours', 'application_charge')
    def _compute_fee(self):
        for line in self:
            price = line.no_of_hours * line.application_charge
            line.update({
                'fee_amount': price
            })

    case_id = fields.Many2one('case.sheet', 'Case Sheet')
    slno = fields.Integer('No')
    product_id = fields.Many2one('product.product', 'Product')
    description = fields.Text(string='Description')

    no_of_hours = fields.Float('Qty')
    application_charge = fields.Float('Charge per Application')
    fee_amount = fields.Float(compute='_compute_fee', string='Fee', store=True)


class CaseAssignmentHistory(models.Model):
    _name = 'case.assignment.history'
    _order = 'date'
    _description = 'Case Sheet Assignment History'

    date=fields.Date('Date', default=time.strftime('%Y-%m-%d'))
    name= fields.Text('Description')
    case_id=fields.Many2one('case.sheet','Case Sheet')

    # _defaults = {
    #     'date':time.strftime('%Y-%m-%d'),
    #     }

CaseAssignmentHistory()
#
#
#Assignee Tasks
class CaseTasksLine(models.Model):
    _name = 'case.tasks.line'
    _order = 'slno'
    _description = 'Tasks Assignment for a Case Sheet'

#sunil
#    @api.model
#    def default_get(self,fields_list):
#        if not self._context:
#            context = {}
#        global line_count_slno
#        line_count_slno +=1
#        res = super(CaseTasksLine, self).default_get(fields_list)
#        return res

#  old code  @api.onchange('count','target_field','recep_date')
    @api.onchange('days','planned_completion_date','start_date')
    def onchange_cnt(self):
        for line in self:
            return_date = (datetime.strptime(line.start_date, '%Y-%m-%d') + timedelta(days=line.days)).strftime('%Y-%m-%d')
            return_date = self.env['hr.holidays.public'].get_next_working_day(return_date)
            # val = { line.planned_completion_date: str(return_date)}
            val = {'planned_completion_date': str(return_date)}
            return {'value': val}

    @api.multi
    def action_add_timesheet(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('legal_e', 'add_timesheet_form')
        view_id = view_ref[1] if view_ref else False
        # context = self._context.copy()
        # context.update({'default_task_id':self.id,'default_case_id':self.case_id.id})
        return {
            'name': _('Add Timesheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'add.timesheet',
            'type': 'ir.actions.act_window',
            'context':({'default_task_id':self.id,'default_case_id':self.case_id.id}),
            'target': 'new',
        }

    @api.multi
    def update_days(self):
        for obj in self:
            days = (datetime.strptime(obj.planned_completion_date, '%Y-%m-%d') - datetime.strptime(obj.start_date, '%Y-%m-%d')).days
            # self.write([obj.id], {'days':days})
            obj.write({'days':days})
        return True

    @api.multi
    def _get_default_assign_to(self):
        ret = False
        if 'assignee_id' in self._context and self._context['assignee_id']:
            return self._context['assignee_id']
        return ret

    @api.multi
    def _set_color_state(self):
        res = {}
        for line in self:
            if line.planned_completion_date < time.strftime('%Y-%m-%d'):
                res[line.id]='before'
            else:
                res[line.id]= 'after'
        return res

    @api.multi
    @api.depends('task_id')
    def _get_state_task(self):
        for task in self:
            stage = task.task_id and task.task_id.stage_id.name or 'New'
            #task.task_id.stage_id.state=stage
            fp_id=self.env['assignment.wise'].search([('name','=',task.id)])
            if fp_id:
               fp_id.write({'state':stage})
            task.state = stage
        return stage
    
    case_id= fields.Many2one('case.sheet','Tasks Assignment Reference', copy=False)
    name= fields.Many2one('task.master', 'Task Name', required=True)
    start_date= fields.Date('Start Date', default=lambda self: (datetime.strptime(str(self.env['hr.holidays.public'].get_next_working_day(time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'))
#    planned_completion_date= fields.Date('End Date')
    planned_completion_date= fields.Date('End Date',default=lambda s: (datetime.strptime(str(s.env['hr.holidays.public'].get_next_working_day(time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'))
    days= fields.Integer('Days')
    slno=fields.Integer(string='Sl no')
    assignee_id= fields.Many2one('hr.employee','Assignee')
    phase_name=fields.Many2one('phase.master','Phase Name', copy=False)
    task_id=fields.Many2one('project.task','Task ID')
    assign_to=fields.Many2one('hr.employee','Assign To',default=lambda s:s._get_default_assign_to())
    state=fields.Char(compute='_get_state_task',string="Status", default='New')
    color_state=fields.Char(compute='_set_color_state',string='Color State')
    old_id=fields.Many2one('case.tasks.line','Old ID', copy=False)
    office_id=fields.Many2one('ho.branch','Office', copy=True) #add office field # Sanal Davis #27/5/15

    # @api.multi
    # def _check_slno_unique(self):
    #     for task_obj in self:
    #         task_ids = self.search([('slno', '=', task_obj.slno), ('case_id', '=', task_obj.case_id.id),('id', '!=', task_obj.id)])
    #         if task_ids:
    #             return False
    #     return True

    # _constraints = [
    #     (_check_slno_unique, "\nError!\n\n'Sl no' must be unique", ['case_id', 'slno'])
    # ]

    # Regenerate sequence of slno
    # @api.onchange('slno', 'case_id')
    # def _compute_slno(self):
    #     for case in self.mapped('case_id'):
    #         count_task = 1
    #         for line in case.tasks_lines:
    #             line.slno = count_task
    #             count_task += 1

    # Starting Sanal Davis  #27/5/15
    @api.onchange('assign_to')
    def onchange_office(self):
        '''
        This function writes the office field value
        '''
        employee_pool = self.env['hr.employee']
        employee = employee_pool.browse(self.assign_to.id)
        if self.assign_to:
            office_id = employee.ho_branch_id.id or False
        else:
            office_id = False
        return {'value': {'office_id': office_id}}
    # Ending

    @api.multi
    def copy_data(self, default=None):
        default = default or {}
#        start_date = time.strftime('%Y-%m-%d')
        start_date = fields.Date.today()
        return_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=self.days)).strftime('%Y-%m-%d')
#        return_date = self.env['hr.holidays.public'].get_next_working_day(return_date)
        default.update({
            'state':'New',
            'task_id':False,
            'start_date': start_date,
            'planned_completion_date': return_date,
            })
        return super(CaseTasksLine, self).copy_data(default)

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return res
        for task_line in self:
            res.append((task_line.id,task_line.name.name))
        return res

    @api.onchange('planned_completion_date','days', 'start_date')
    def check_for_holiday(self):
        vals = {}
        for line in self:
            vals['planned_completion_date'] = line.planned_completion_date
            year = time.strftime('%Y')
            holiids = self.env['hr.holidays.public'].search([('year','=',year)])
            public_holidays = []
            for holi in holiids:
                for line in holi.line_ids:
                    public_holidays.append(line.date)
            if len(line.planned_completion_date)>10:
                line.planned_completion_date = line.planned_completion_date[:10]
            if datetime.strptime(line.planned_completion_date, '%Y-%m-%d').weekday() == 6 or (len(public_holidays)>0 and line.planned_completion_date in public_holidays):
                vals['planned_completion_date'] = time.strftime('%Y-%m-%d')
                warning = {
                           'title': _('Error!'),
                           'message' : _('Selected Day is a Holiday, Please select another Day!')
                        }
                ret = line.onchange_cnt()
                return {'value': ret['value'], 'warning': warning}
            return {'value':vals}

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.task_id:
                # self.env['project.task'].unlink([obj.task_id.id])
                obj.task_id.unlink()
        retvals = super(CaseTasksLine, self).unlink()
        global line_count_slno
        return retvals

    @api.model
    def create(self,vals):
        if self._context is None:
            context = {}
        retvals = super(CaseTasksLine, self).create(vals)
        for line in retvals:
            if line.case_id and line.case_id.state not in ['new', 'waiting']:
                line.case_id.confirm_casesheet()
                # self.env['case.sheet'].confirm_casesheet([line.case_id.id])
        vals['task_new_id'] = retvals
        vals = self.env['assignment.wise'].update_related_task_for_cost_Details(vals)
        vals = self.env['fixed.price.stages'].update_related_task_for_cost_Details(vals)

        return retvals

    @api.multi
    def write(self,vals):
        retvals = super(CaseTasksLine, self).write(vals)
        user_pool = self.env['res.users']
        csm = user_pool.has_group('legal_e.group_legal_e_client_service_manager')
        # csm_super_id = uid
        if csm:
            csm_super_id = SUPERUSER_ID
        for line in self:
            assigned = self.env['hr.employee'].browse(line.assign_to.id)
            if line.case_id and line.case_id.project_id:
#                project = self.env['project.project'].browse(line.case_id.project_id.id)
                if not assigned.user_id.id in line.case_id.project_id.members.ids:
                    line.case_id.project_id.write({'members':[(4, assigned.user_id.id)]})
                    line.case_id.write({'members':[(4, assigned.user_id.id)]})
                res={}
                if 'planned_completion_date' in vals:
                    res['date_deadline'] = vals['planned_completion_date']
                    if vals['planned_completion_date'] >= time.strftime('%Y-%m-%d'):
                        task_type_ids = self.env['project.task.type'].search([('state','=','draft')])
                        if task_type_ids:
                            res['stage_id'] = task_type_ids[0]
                        res['state'] = 'draft'
                    else:
                        task_type_ids = self.env['project.task.type'].search([('state','=','pending')])
                        if task_type_ids:
                            res['stage_id'] = task_type_ids[0]
                        res['state'] = 'pending'
                    res['planned_hours'] = line.days*8
                    res['date_end'] = vals['planned_completion_date']
                if 'assign_to' in vals:
                    res['assignee_id'] = vals['assign_to']
#                if line.task_id and line.task_id.state != 'done':
#                    self.env['project.task'].write([line.task_id.id])

                if vals.get('state', False) == 'Completed':
                    tasks_ids = self.search([('case_id', '=', line.case_id.id), ('id', '!=', line.id)])
                    test = {}
                    for task_obj in tasks_ids:
                        if task_obj.state in ('Pending', 'New', 'In Progress'):
                            test.update({int(task_obj.slno): task_obj})
                    keys = test.keys()
                    key=sorted(keys)
                    list_key=list(key)
                    if key:
                        task_type_ids = self.env['project.task.type'].search([('state','=','open')],order='sequence',limit=1)
                        if task_type_ids and test[list_key[0]].task_id.state not in ('pending', 'done', 'cancelled'):
                            test[list_key[0]].task_id.write({'stage_id': task_type_ids.id, 'state': 'open'})
    #                         res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'email_template_assignee_task')
    #                         res_id = res and res[1] or False
    #                         if test[key[0]].task_id.assignee_id and test[key[0]].task_id.assignee_id.work_email:
    #                             self.pool.get('email.template').send_mail(cr, uid, res_id, test[key[0]].task_id.id, force_send=True, context=context)


        return retvals


#Other Associates
class OtherAssociate(models.Model):
    _name='other.associate'
    _description = 'Other Associate'

    case_id=fields.Many2one('case.sheet','File Number')
    name=fields.Many2one('res.partner','Associate')

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return res
        for line in self:
            res.append((line.id,line.name.name))
        return res

OtherAssociate()

#Associate Tasks
class AssociateTasksLine(models.Model):
    _name = 'associate.tasks.line'
    _order = 'slno,days'
    _description = 'Assciate Tasks for a Case Sheet'

    @api.model
    def default_get(self,fields_list):
        if not self._context:
            context = {}
        global line_count_slno
        line_count_slno +=1
        res = super(AssociateTasksLine, self).default_get(fields_list)
        return res

#    @api.onchange('count','target_field','recep_date')
    @api.onchange('days','planned_completion_date','start_date')
    def onchange_cnt(self):
        for line in self:
            return_date = (datetime.strptime(line.start_date, '%Y-%m-%d') + timedelta(days=line.days)).strftime('%Y-%m-%d')
            return_date = self.env['hr.holidays.public'].get_next_working_day(return_date)
            val = {
                line.planned_completion_date: str(return_date)
            }
            return {'value': val}

    @api.multi
    def _get_default_assign_to(self):
        ret = False
        if 'associate_id' in self._context and self._context['associate_id'] and len(self._context['associate_id'])>0:
            if self._context['associate_id'][0][0] == 0:
                return self._context['associate_id'][0][2]['name']
            elif self._context['associate_id'][0][0] == 4:
                obj = self.env['other.associate'].browse(self._context['associate_id'][0][1])
                return obj.name.id

        return ret

    @api.multi
    def _set_color_state(self):
        res = {}
        for line in self:
            if line.planned_completion_date < time.strftime('%Y-%m-%d'):
                res[line.id]='before'
            else:
                res[line.id]= 'after'
        return res

    @api.multi
    def _get_state_task(self):
        for task in self:
            stage = task.task_id and task.task_id.stage_id.name or 'New'
#            res[task.id] = stage
            task.state=stage
        return stage


    case_id= fields.Many2one('case.sheet','Associate Tasks Assignment Reference')
    name=fields.Many2one('task.master', 'Task Name', required=True)
    start_date=fields.Date('Start Date', default=lambda s: (datetime.strptime(str(s.env['hr.holidays.public'].get_next_working_day(time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),)
    planned_completion_date= fields.Date('Task Date', default=lambda s: (datetime.strptime(str(s.env['hr.holidays.public'].get_next_working_day(time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),)
    days=fields.Integer('Days')
    slno=fields.Integer('Sl no')
    associate_id=fields.Many2one('hr.employee','Associate')
    phase_name=fields.Many2one('phase.master','Phase Name')
    assign_to_in_associate=fields.Many2one('res.partner','Assign To', default=lambda s:s._get_default_assign_to())
    task_id=fields.Many2one('project.task','Task ID')
    state=fields.Char(compute='_get_state_task',string="Status")
    color_state=fields.Char(compute='_set_color_state',string='Color State')
    old_id=fields.Many2one('associate.tasks.line','Old ID')

    # _defaults = {
    #     'assign_to_in_associate': lambda s, cr, uid, c:s._get_default_assign_to(cr, uid, c),
    #     'planned_completion_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
    #     'start_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
    #     'state':'New',
    # }

    @api.multi
    def copy_data(self, default=None):
        default = default or {}
        start_date = time.strftime('%Y-%m-%d')
        # data_obj  = self
        return_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=self.days)).strftime('%Y-%m-%d')
        return_date = self.env['hr.holidays.public'].get_next_working_day(return_date)
        default.update({
            'state':'New',
            'task_id':False,
            'start_date': start_date,
            'planned_completion_date': return_date,
            })
        return super(AssociateTasksLine, self).copy_data(default)

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return res
        for task_line in self:
            res.append((task_line.id,task_line.name.name))
        return res

    @api.onchange('planned_completion_date','days', 'start_date')
    def check_for_holiday(self):
        vals = {}
        for line in self:
            vals['planned_completion_date'] = line.planned_completion_date
            year = time.strftime('%Y')
            holiids = self.env['hr.holidays.public'].search([('year','=',year)])
            public_holidays = []
            for holi in holiids:
                for line in holi.line_ids:
                    public_holidays.append(line.date)
            if len(line.planned_completion_date)>10:
                line.planned_completion_date = line.planned_completion_date[:10]
            if datetime.strptime(line.planned_completion_date, '%Y-%m-%d').weekday() == 6 or (len(public_holidays)>0 and line.planned_completion_date in public_holidays):
                vals['planned_completion_date'] = time.strftime('%Y-%m-%d')
                warning = {
                           'title': _('Error!'),
                           'message' : _('Selected Day is a Holiday, Please select another Day!')
                        }
                ret = line.onchange_cnt()
                return {'value': ret['value'], 'warning': warning}
            return {'value':vals}

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.task_id:
                self.env['project.task'].unlink([obj.task_id.id])
        retvals = super(AssociateTasksLine, self).unlink()
        global line_count_slno
        return retvals

    @api.model
    def create(self, vals):
        if self._context is None:
            context = {}
        retvals = super(AssociateTasksLine, self).create(vals)
        casesheet = self.env['case.sheet'].browse(vals['case_id'])
        if casesheet.project_id:
            for line in casesheet.associate_tasks_lines:
                phase_id = False
                # if line.phase_name:
                #     phase_ids = self.env['project.phase'].search([('name','=',line.phase_name.name),('project_id','=',casesheet.project_id.id)])
                #     if len(phase_ids)<=0:
                #         phase_id=self.env['project.phase'].create({'name':line.phase_name.name,'project_id':casesheet.project_id.id, 'product_uom':6,'duration':(line.days or 0)})
                #     else:
                #         phase_id = phase_ids[0]
                #         phase = self.env['project.phase'].browse(phase_id)
                #         duration = (line.days or 0) + (phase.duration or 0)
                #         self.env['project.phase'].write([phase_id],{'duration':duration})
                if not line.task_id:
                    task_id = self.env['project.task'].create({'project_id':casesheet.project_id.id,'phase_id':phase_id,'name':line.name.id,'task_for':'associate','other_assignee_id':line.assign_to_in_associate.id,'date_deadline':line.planned_completion_date, 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8})
                    line.write({'task_id':task_id.id})
                    # self.env['associate.tasks.line'].write([line.id], {'task_id':task_id})

        return retvals

    @api.multi
    def write(self, vals):
        retvals = super(AssociateTasksLine, self).write(vals)
        line = self.browse(self.ids[0])
        res={}
        if 'planned_completion_date' in vals:
            res['date_deadline'] = vals['planned_completion_date']
            if vals['planned_completion_date'] >= time.strftime('%Y-%m-%d'):
                task_type_ids = self.env['project.task.type'].search([('state','=','draft')])
                if task_type_ids:
                    res['stage_id'] = task_type_ids[0]
                res['state'] = 'draft'
            else:
                task_type_ids = self.env['project.task.type'].search([('state','=','pending')])
                if task_type_ids:
                    res['stage_id'] = task_type_ids[0]
                res['state'] = 'pending'

            res['planned_hours'] = line.days*8
            res['date_end'] = vals['planned_completion_date']
        if 'assign_to_in_associate' in vals:
            res['other_assignee_id'] = vals['assign_to_in_associate']
        if line.task_id:
            line.task_id.write(res)
            # self.env['project.task'].write([line.task_id.id],res)


        return retvals

AssociateTasksLine()


#Client Tasks
class ClientTasksLine(models.Model):
    _name = 'client.tasks.line'
    _order = 'slno'
    _description = 'Tasks Assignment for a Case Sheet'

    @api.model
    def default_get(self, fields_list):
        if not self._context:
            context = {}
        global line_count_slno
        line_count_slno +=1
        res = super(ClientTasksLine, self).default_get(fields_list)
        return res

    @api.onchange('planned_completion_date')
    def onchange_cnt(self):
        for line in self:
            return_date = (datetime.strptime(line.planned_completion_date, '%Y-%m-%d')).strftime('%Y-%m-%d')
            return_date = self.env['hr.holidays.public'].get_next_working_day(return_date)
            val = {
                line.planned_completion_date: str(return_date)
            }
        return {'value': val}

    # @api.multi
    # def _get_default_assign_to(self):
    #     ret = False
    #     if 'client_id' in self._context and self._context['client_id']:
    #         return self._context['client_id']
    #     return ret

    # @api.multi
    # def _set_color_state(self):
    #     res = {}
    #     for line in self:
    #         if line.planned_completion_date < time.strftime('%Y-%m-%d'):
    #             res[line.id]='before'
    #         else:
    #             res[line.id]= 'after'
    #     return res

    # @api.multi
    # def _get_state_task(self):
    #     res={}
    #     for task in self:
    #         stage = task.task_id and task.task_id.stage_id.name or 'New'
    #         res[task.id] = stage
    #     return res

    case_id=fields.Many2one('case.sheet','Tasks Assignment Reference')
    slno=fields.Integer('Sl no')
    name=fields.Char('Task Name', required=True)
    # name=fields.Many2one('task.master', 'Task Name', required=True)
    user_id=fields.Many2one('res.users', 'Assignee To')
    planned_completion_date= fields.Date('Task Date', default=lambda s: (datetime.strptime(str(s.env['hr.holidays.public'].get_next_working_day(time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'))
    # assign_to_in_client=fields.Many2one('res.partner','Assign To', default=lambda self:self._get_default_assign_to())
    # start_date=fields.Date('Start Date', default=lambda s: (datetime.strptime(str(s.env['hr.holidays.public'].get_next_working_day(time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'))
    # days=fields.Integer('Days')
    # phase_name=fields.Many2one('phase.master','Phase Name')
    task_id=fields.Many2one('project.task','Task ID')
    # state=fields.Char(compute='_get_state_task',string="Status")
    # color_state=fields.Char(compute='_set_color_state',string='Color State')
    old_id=fields.Many2one('client.tasks.line','Old ID')
    # no_of_hours = fields.Float('No Of Hours')
    # account_analytic_line_id = fields.Many2one('account.analytic.line', 'Time Sheet', track_visibility='onchange')

    # _defaults = {
    #     'assign_to_in_client': lambda s, cr, uid, c:s._get_default_assign_to(cr, uid, c),
    #     'planned_completion_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
    #     'start_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
    #     'state':'New',
    #
    # }

    @api.multi
    def copy_data(self, default=None):
        default = default or {}
        start_date = time.strftime('%Y-%m-%d')
        # data_obj  = self.browse(cr, uid, ids, context=context)
#        return_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=self.days)).strftime('%Y-%m-%d')
 #       return_date = self.env['hr.holidays.public'].get_next_working_day(return_date)
        default.update({
            # 'state':'New',
            'task_id':False,
  #          'planned_completion_date': return_date,
            })
        return super(ClientTasksLine, self).copy_data(default)

    @api.onchange('planned_completion_date')
    def check_for_holiday(self):
        vals = {}
        for line in self:
            vals['planned_completion_date'] = line.planned_completion_date
            year = time.strftime('%Y')
            holiids = self.env['hr.holidays.public'].search([('year','=',year)])
            public_holidays = []
            for holi in holiids:
                for line in holi.line_ids:
                    public_holidays.append(line.date)
            if len(line.planned_completion_date)>10:
                line.planned_completion_date = line.planned_completion_date[:10]
        # if datetime.strptime(plandate, '%Y-%m-%d').weekday() == 6 or (len(public_holidays)>0 and line.planned_completion_date in public_holidays):
        if (len(public_holidays)>0 and line.planned_completion_date in public_holidays):
            vals['planned_completion_date'] = time.strftime('%Y-%m-%d')
            warning = {
                       'title': _('Error!'),
                       'message' : _('Selected Day is a Holiday, Please select another Day!')
                    }
            ret = line.onchange_cnt()
            return {'value': ret['value'], 'warning': warning}
        return {'value':vals}

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.task_id:
                obj.task_id.unlink()
                # self.env['project.task'].unlink([obj.task_id.id])
        retvals = super(ClientTasksLine, self).unlink()
        global line_count_slno
        return retvals

    # COMMENT THIS CODE BECAUSE DONT WANT PROJECT TASK CREATE
    # @api.model
    # def create(self, vals):
    #     retvals = super(ClientTasksLine, self).create(vals)
    #     casesheet = self.env['case.sheet'].browse(vals['case_id'])
    #     if casesheet.project_id:
    #         for line in casesheet.client_tasks_lines:
    #             phase_id = False
    #             if not line.task_id:
    #                 task_id = self.env['project.task'].create({
    #                     'project_id':casesheet.project_id.id,
    #                     'phase_id':phase_id,
    #                     'name':line.name.name,
    #                     'task_for':'associate',
    #                     'date_deadline':line.planned_completion_date,
    #                     # 'client_id':casesheet.client_id.id,
    #                     'sequence':line.slno,
    #                     # 'date_start':line.start_date,
    #                     # 'date_end':line.planned_completion_date,
    #                     # 'planned_hours':line.days*8
    #                 })
    #                 line.write({'task_id': task_id.id})
    #                 # self.env['client.tasks.line'].write([line.id], {'task_id':task_id})
    #     # if retvals and retvals.no_of_hours > 0 and casesheet.project_id:
    #     #     account_analytic_line_id = self.env['account.analytic.line'].create(
    #     #         {'date': retvals.planned_completion_date, 'project_id': casesheet.project_id.id, 'name': retvals.name.name,
    #     #          'unit_amount': retvals.no_of_hours})
    #     #     if account_analytic_line_id:
    #     #         retvals.account_analytic_line_id = account_analytic_line_id.id
    #     return retvals

    # COMMENT THIS CODE BECAUSE DONT WANT PROJECT TASK UPDATE
    # @api.multi
    # def write(self,vals):
    #     retvals = super(ClientTasksLine, self).write(vals)
    #     # line = self.ids[0]
    #     line = self.browse(self.ids[0])
    #     res={}
    #     if 'planned_completion_date' in vals:
    #         res['date_deadline'] = vals['planned_completion_date']
    #
    #         if vals['planned_completion_date'] >= time.strftime('%Y-%m-%d'):
    #             task_type_ids = self.env['project.task.type'].search([('state','=','draft')])
    #             if task_type_ids:
    #                 res['stage_id'] = task_type_ids[0]
    #             res['state'] = 'draft'
    #         else:
    #             task_type_ids = self.env['project.task.type'].search([('state','=','pending')])
    #             if task_type_ids:
    #                 res['stage_id'] = task_type_ids[0]
    #             res['state'] = 'pending'
    #         res['planned_hours'] = line.days*8
    #         res['date_end'] = vals['planned_completion_date']
    #     # if 'assign_to_in_client' in vals:
    #     #     res['client_id'] = vals['assign_to_in_client']
    #     if line.task_id:
    #         line.task_id.write(res)
    #         # self.env['project.task'].write([line.task_id.id],res)
    #     return retvals

    @api.multi
    def action_complete_task_timesheet(self):
        self.ensure_one()
        # view_ref = self.env['ir.model.data'].get_object_reference('legal_e', 'complete_task_timesheet_form')
        # view_id = view_ref[1] if view_ref else False
        view_id = self.env.ref('legal_e.complete_task_timesheet_form').id
        return {
            'name': _('Complete Task Timesheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'complete.task.timesheet',
            'type': 'ir.actions.act_window',
            'context': ({'default_name': self.name, 'default_to_do_id': self.id, 'default_case_id': self.case_id.id}),
            'target': 'new',
        }



class AssociatePayment(models.Model):
    _name = 'associate.payment'

    case_id=fields.Many2one('case.sheet','File Number')
    name=fields.Many2one('associate.tasks.line','Task Related', required=True)
    date= fields.Date('Date')
    description=fields.Char('Description',size=1024)
    amount=fields.Float('Amount', required=True)
    invoiced=fields.Boolean('Invoiced', readonly=True)
    # state':fields.related('name','state',type='selection',selection=[('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Pending','Pending'),('Completed','Completed'),('Invoiced','Invoiced')],string="Status")
    # state = fields.Selection([
    #     ('New', 'New'),
    #     ('In Progress', 'In Progress'),
    #     ('Hold', 'Hold'),
    #     ('Pending', 'Pending'),
    #     ('Completed', 'Completed'),
    #     ('Invoiced', 'Invoiced')], string='Status',related='name.state')
    invoice_id=fields.Many2one('account.invoice', 'Invoice ID')
    associate_id=fields.Many2one('other.associate','Associate')
    po_id=fields.Many2one('purchase.order','Purchase Order')
    old_id=fields.Many2one('associate.payment','Old ID')

    @api.multi
    def copy_data(self, default=None):
        default = default or {}
        default.update({
            'invoiced':False
        })
        return super(AssociatePayment, self).copy_data(default)

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return res
        for line in self:
            res.append((line.id,line.name.name))
        return res

    @api.multi
    def view_invoice_task(self):
        obj = self.ids[0]
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('account', 'invoice_supplier_form')
        except ValueError as e:
            view_id = False
        return {
            'name': _('Supplier Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.invoice_id.id,
        }


    @api.multi
    def invoice_associate_task(self):
        if not self._context:
            context = {}
        for line in self:
            if line.associate_id:
                partner_id = line.associate_id.name
                acc_id = partner_id.property_account_payable.id
                name=line.name.name.name
                if line.name.name.product_id:
                    name= line.name.name.name
                vals = {
                    'partner_id': partner_id.id,
                    'account_id':acc_id,
                    'type':'in_invoice',
                    'origin': line.case_id.name,
                    'case_id': line.case_id.id,
                    'invoice_line':[(0, 0, {
                        'name': line.description and line.description or 'Payment for the Task ' + name,
                        'quantity':1.00,
                        'price_unit':line.amount,
                        'type':'in_invoice',
                        'account_analytic_id': line.case_id.project_id.analytic_account_id.id,
                        })]
                    }
                inv_id = self.env['account.invoice'].create(vals)
                # self.write([line.id], {'invoiced':True,'invoice_id':inv_id})
                line.write({'invoiced':True,'invoice_id':inv_id})
        return True


class TaskTemplateLine(models.Model):
    _name = 'task.template.line'

    template_id=fields.Many2one('task.template','Template Reference')
    name=fields.Many2one('task.master', 'Task', required=True)
    days= fields.Integer('Days')
    slno=fields.Integer('Sl no')
    phase_name=fields.Many2one('phase.master','Phase Name')
    type=fields.Selection([('assignee','Assignee'),('associate','Associate'),('client','Client')],'Task For')


class TaskTemplate(models.Model):
    _name = 'task.template'

    name=fields.Selection([
        ('civillitigation', 'Civil Litigation'),
        ('criminallitigation', 'Criminal Litigation'),
        ('non_litigation', 'Non Litigation'),
        ('arbitration', 'Arbitration'),
        ('execution', 'Execution'),
        ('mediation', 'Mediation')], 'Type of Work', required=True)
    casetype_id= fields.Many2one('case.master','Case Type', required=True)
    tasks_lines=fields.One2many('task.template.line','template_id','Task Template Lines')


#     def create(self, cr, uid, vals, context=None):
#         retids = self.search(cr, uid, [('name','=',vals['name']),('casetype_id','=',vals['casetype_id'])])
#         if len(retids)>0:
#             lineids = self.pool.get('task.template.line').search(cr, uid, [('name','=',vals['tasks_lines'][0][2]['name']),('template_id','=',retids[0])])
#             if len(lineids)>0:
#                 self.pool.get('task.template.line').write(cr, uid, [lineids[0]], {'days':vals['tasks_lines'][0][2]['days'],'slno':vals['tasks_lines'][0][2]['slno'],'phase_name':vals['tasks_lines'][0][2]['phase_name']})
#             else:
#                 self.pool.get('task.template.line').create(cr, uid, {'template_id':retids[0],'name':vals['tasks_lines'][0][2]['name'],'phase_name':vals['tasks_lines'][0][2]['phase_name'],'slno':vals['tasks_lines'][0][2]['slno'],'days':vals['tasks_lines'][0][2]['days']})
#             return retids[0]
#         else:
#             retvals = super(task_template, self).create(cr, uid, vals, context=context)
#             return retvals

TaskTemplate()

class CaseTaskLine(models.Model):
    _name = 'case.task.line'
    _inherit = ['mail.thread']
    _description = 'Task Assignment for a Case Sheet'

    @api.multi
    def _get_task_amount(self):
        res = {}
        for line in self:
            #we may not know the level of the parent at the time of computation, so we
            # can't simply do res[account.id] = account.parent_id.level + 1
            amount = 0.0
            if line.amount:
                amount = line.amount * line.hours_spent
            res[line.id] = amount
        return res

    case_id= fields.Many2one('case.sheet', 'Task Assignment Reference')
    name= fields.Many2one('task.master', 'Task Name', required=True)
    start_date= fields.Date('Start Date',required=True)
    plan_completion_date= fields.Date('Planned Completion Date')
    state= fields.Selection([
        ('new','New'),
        ('inprogress','InProgress'),
        ('completedduebill','Completed & Due for Billing'),
        ('billed','Bill Generated'),
        ('paid','Paid'),
        ('done','Closed')],'Status', required=True, default='new')
    assignee_id= fields.Many2one('hr.employee', 'Assignee', required=True)
    hours_spent= fields.Float('Spent Hours',readonly=True)
    activity_lines= fields.One2many('task.activity.line', 'task_id', 'Activity Assignment Lines')
    amount=fields.Float(compute='_get_task_amount', string='Amount')
    # meeting_id=fields.Many2one('crm.meeting','Meeting')

    # _defaults = {
    # 	'state':'new',
    # }



    @api.model
    def default_get(self, fields_list):
        if not self._context:
            context = {}
        res = super(CaseTaskLine, self).default_get(fields_list)
        if 'assignee_id' in context:
            res.update({'assignee_id':context['assignee_id']})
        return res

    @api.model
    def create(self, vals):
        retvals = super(CaseTaskLine, self).create(vals)
        line = self.browse(retvals)
        #To Create a Meeting in CRM Meetings
        meeting_obj = self.env['crm.meeting']
        start_dt = datetime.strptime(line.start_date, '%Y-%m-%d')
        end_dt = (datetime.strptime(line.start_date, '%Y-%m-%d') + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        duration = 1
        if line.plan_completion_date:
            end_dt = datetime.strptime(line.plan_completion_date, '%Y-%m-%d')
            duration = (end_dt - start_dt).days * 24
        meeting_vals = {
                    'name': line.name.name,
                    'user_id': (line.assignee_id.user_id.id or False),
                    'date': line.start_date,
                    'date_deadline': end_dt,
                    'duration':duration,
                    'state': 'open',            # to block that meeting date in the calendar
                }
        meeting_obj.create(meeting_vals)
        if line.assignee_id.user_id and line.assignee_id.user_id.partner_id:
            post_values =  {
                'partner_ids': [line.assignee_id.user_id.partner_id.id],
                'subject': '%s Task Assigned for you for the Case %s' % (line.name.name,line.case_id.name),
                'body': '"%s" Task Assigned for you for the Case "%s" and the Start Date is %s.' % (line.name.name, line.case_id.name, line.start_date),
                }
            subtype = 'mail.mt_comment'
            self.message_post([line.id], type='comment', subtype=subtype, **post_values)

        self.env['tm.line'].create({'case_id':vals['case_id'],'task_id':retvals,'assignee_id':vals['assignee_id'],'hours_spent':('hours_spent' in vals and vals['hours_spent'] or False),'name':line.name.id})

        return retvals

    @api.multi
    def write(self, vals):
        retvals = super(CaseTaskLine, self).write(vals)
        line = self.ids[0]
        tmlines = self.env['tm.line'].search([('task_id','=',self.ids)])
        if tmlines:
            for tmline in tmlines:
                self.env['tm.line'].write([tmline.id], {'hours_spent':line.hours_spent, 'state':line.state})
        return retvals


class TmLineInvoice(models.Model):
    _name = 'tm.line.invoice'

    tm_line_id= fields.Many2one('tm.line', 'Task Assignment Reference')
    name=fields.Many2one('account.invoice','Invoice ID')
    hours=fields.Float('Billed Hours')


class TmLine(models.Model):
    _name = 'tm.line'
    _description = 'Time and Material Amount for a Task'

    @api.multi
    def _get_task_amount(self):
        res = {}
        for line in self:
            amount = 0.0
            if line.case_id.tm_per_hour:
                amount = line.case_id.tm_per_hour * line.hours_spent
                res[line.id] = amount
        return res

    @api.multi
    def _get_hours_spent(self):
        res = {}
        for line in self:
            work_ids = self.env['project.task.work'].search([('task_id','=',line.name.task_id.id)])
            hours = 0.0
            for wline in work_ids:
                hours += wline.hours
            res[line.id] = hours
        return res

    @api.multi
    def _get_remaining_hours(self):
        res = {}
        hours = 0.0
        for line in self:
            hours = (line.hours_spent or 0.0) - (line.billed_hours or 0.0)
            res[line.id] = hours
        return res

    @api.multi
    def _get_invoiced_total(self):
        res = {}

        for line in self:
            total = 0.0
            for invid in line.invoice_ids:
                inv = self.env['account.invoice'].browse(invid.name.id)
                total += inv.amount_total
            res[line.id] = total
        return res

    @api.multi
    def _get_invoiced_balance(self):
        res = {}

        for line in self:
            residual = 0.0
            for invid in line.invoice_ids:
                inv = self.env['account.invoice'].browse(invid.name.id)
                residual += inv.residual
            res[line.id] = residual
        return res

    @api.multi
    def _get_invoiced_state(self):
        res = {}
        for line in self:
            state = False
            if line.invoice_id:
                states = {'draft':'Draft','proforma':'Pro-forma','proforma2':'Pro-forma','open':'Open','sent_for_validate':'Sent for Validate','validation_reject':'Validation Rejected','paid':'Paid','cancel':'Cancelled'}
                inv = self.env['account.invoice'].browse(line.invoice_id.id)
                state = states[inv.state]
            res[line.id] = state
        return res

    @api.multi
    def view_invoice_task(self):
        obj = self.ids[0]
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
        except ValueError as e:
            view_id = False
        if len(obj.invoice_ids)==1:
            return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': obj.invoice_ids[0].name.id,
            }
        else:
            lst = []
            for dt in obj.invoice_ids:
                lst.append(dt.name.id)
            return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'domain': "[('id','in',("+str(lst)+"))]",
                'view_id': False,
                'context':{},
            }

    @api.multi
    def view_case_sheet(self):
        obj = self.ids[0]
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'case_sheet_form')
        except ValueError as e:
            view_id = False
        return {
            'name': _('Case Sheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'case.sheet',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.case_id.id,
        }

    case_id= fields.Many2one('case.sheet', 'Case Sheet No.')
    name=fields.Many2one('case.tasks.line','Task Related', required=True,readonly=False,)
    hours_spent=fields.Float(compute='_get_hours_spent',string='Total Hours')
    hours_planned= fields.Float('Initially Planned Hour(s)',readonly=True)
    amount=fields.Float(compute='_get_task_amount', string='Amount')
    out_of_pocket_amount= fields.Float('Out of Pocket Expense')
    state= fields.Selection([
        ('New','New'),
        ('In Progress','In Progress'),
        ('Hold','Hold'),
        ('Pending','Pending'),
        ('Completed','Completed'),
        ('Invoiced','Invoiced')],'Status', readonly=True, default='New')
    invoiced=fields.Boolean('Invoiced')
    invoice_ids=fields.One2many('tm.line.invoice', 'tm_line_id', 'Invoice IDs')
    inv_total_amt=fields.Float(compute='_get_invoiced_total',string='Total INV Amt',readonly=True)
    inv_balance_amt=fields.Float(compute='_get_invoiced_balance',string='Balance INV Amt',readonly=True)
    billed_hours= fields.Float('Billed Hours')
    remaining_hours= fields.Float(compute='_get_remaining_hours',string='Hours to Bill')

    @api.multi
    def invoice_task(self):
        if not self._context:
            context = {}
        for line in self:
            partner_id = line.case_id.client_id.id
            p = self.env['res.partner'].browse(partner_id)
            acc_id = p.property_account_receivable.id
            context.update({'type':'out_invoice'})
            pettyids = self.env['account.account'].search([('name','=','PETTYCASH')])
            pettycash_acc_id = False
            if pettyids and len(pettyids) >0:
                pettycash_acc_id = pettyids[0]
            product_id=False
            prod_acc_id = False
            diff = line.hours_spent - (line.billed_hours or 0.0)
            diff_hours = (line.billed_hours or 0.0) + diff
            if line.name.name.product_id:
                product_id = line.name.name.product_id.id
                if line.name.name.product_id.property_account_income:
                    prod_acc_id = line.name.name.product_id.property_account_income.id
            inv_id = self.env['account.invoice'].create({'partner_id':partner_id,'account_id':acc_id,'invoice_line':[(0, 0, {'product_id':product_id,'name': 'Professional Charges', 'quantity':diff,'price_unit':line.case_id.tm_per_hour,'type':'out_invoice','account_id':prod_acc_id}),(0, 0, {'product_id':False,'name': 'Out of Pocket Expenses', 'quantity':1,'price_unit':line.out_of_pocket_amount,'type':'out_invoice','account_id':pettycash_acc_id})]},context)
            # self.write([line.id], {'invoiced':True,'billed_hours':diff_hours,'invoice_ids':[(0, 0, {'tm_line_id':line.id,'name': inv_id,'hours':diff})]})
            line.write({'invoiced':True,'billed_hours':diff_hours,'invoice_ids':[(0, 0, {'tm_line_id':line.id,'name': inv_id,'hours':diff})]})
        return True


class AssignmentWiseInvoice(models.Model):
    _name = 'assignment.wise.invoice'


    assignment_wise_id=fields.Many2one('assignment.wise', 'Assignment Wise ID')
    name=fields.Many2one('account.invoice','Invoice ID')
    hours=fields.Float('Billed Hours')


AssignmentWiseInvoice()


class AssignmentWise(models.Model):
    _name = 'assignment.wise'
    _description = 'Time and Material Amount for a Task'

    @api.multi
    def _get_task_amount(self):
        res = {}
        for line in self:
            amount = 0.0
            if line.case_hourly_id.tm_per_hour:
                amount = line.case_hourly_id.tm_per_hour * line.hours_spent
                res[line.id] = amount
        return res

    @api.multi
    def _get_hours_spent(self):
        res = {}
        for line in self:
            work_ids = self.env['project.task.work'].search([('task_id','=',line.name.task_id.id)])
            hours = 0.0
            for wline in work_ids:
                hours += wline.hours
            res[line.id] = hours
        return res

    @api.multi
    def _get_remaining_hours(self):
        res = {}
        hours = 0.0
        for line in self:
            hours = (line.hours_spent or 0.0) - (line.billed_hours or 0.0)
            res[line.id] = hours
        return res

    @api.multi
    def _get_invoiced_total(self):
        res = {}

        for line in self:
            total = 0.0
            for invid in line.invoice_ids:
                inv = self.env['account.invoice'].browse(invid.name.id)
                total += inv.amount_total
            res[line.id] = total
        return res

    @api.multi
    def _get_invoiced_balance(self):
        res = {}

        for line in self:
            residual = 0.0
            for invid in line.invoice_ids:
                inv = self.env['account.invoice'].browse(invid.name.id)
                residual += inv.residual
            res[line.id] = residual
        return res

    @api.multi
    def _get_invoiced_state(self):
        res = {}
        for line in self:
            state = False
            if line.invoice_id:
                states = {'draft':'Draft','proforma':'Pro-forma','proforma2':'Pro-forma','open':'Open','paid':'Paid','cancel':'Cancelled'}
                inv = self.env['account.invoice'].browse(line.invoice_id.id)
                state = states[inv.state]
            res[line.id] = state
        return res

    @api.multi
    def view_invoice_task(self):
        obj = self.ids[0]
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
        except ValueError as e:
            view_id = False
        if len(obj.invoice_ids)==1:
            return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': obj.invoice_ids[0].name.id,
            }
        else:
            lst = []
            for dt in obj.invoice_ids:
                lst.append(dt.name.id)
            return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'domain': "[('id','in',("+str(lst)+"))]",
                'view_id': False,
                'context':{},
            }

    @api.multi
    def view_case_sheet(self):
        obj = self.ids[0]
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'case_sheet_form')
        except ValueError as e:
            view_id = False
        return {
            'name': _('Case Sheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'case.sheet',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.case_hourly_id.id,
        }

    @api.onchange('type')
    def onchange_type(self):
        vals = {}
        for line in self:
            if line.type != 'hour_wise':
                vals['billed_hours'] = False
                vals['remaining_hours'] = False
                vals['hours_spent'] = False
            return {'value':vals}

    case_hourly_id= fields.Many2one('case.sheet', 'Case Sheet No.')
    case_fixed_id= fields.Many2one('case.sheet', 'Case Sheet No.')
    name=fields.Many2one('case.tasks.line','Task Related', required=False,readonly=False,)
    description=fields.Char('Description',size=1024)
    type=fields.Selection([('task_wise','Fixed'),('hour_wise','Hourly')],'Type', default=lambda s: 'type' in s and s['type'] or False)
    hours_spent= fields.Float('Hours Spent')
    hours_planned= fields.Float('Initially Planned Hour(s)',readonly=True)
    amount=fields.Float('Amount')
    out_of_pocket_amount= fields.Float('Out of Pocket Expense')
    # 'state':fields.related('name','state',type='selection',selection=[('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Pending','Pending'),('Completed','Completed'),('Invoiced','Invoiced')],string="Status"),
    state = fields.Selection([
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Hold', 'Hold'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Invoiced', 'Invoiced')], string='Status', default='New')
     #related = 'name.name.state')
    invoiced=fields.Boolean('Invoiced')
    invoice_ids=fields.One2many('assignment.wise.invoice', 'assignment_wise_id', 'Invoice IDs')
    inv_total_amt=fields.Float(compute='_get_invoiced_total',string='Total INV Amt',readonly=True)
    inv_balance_amt=fields.Float(compute='_get_invoiced_balance',string='Balance INV Amt',readonly=True)
    billed_hours= fields.Float('Total Invoiced Hours')
    remaining_hours= fields.Float('To be Invoiced Hours')
    old_id=fields.Many2one('assignment.wise','Old ID')
    office_id=fields.Many2one('ho.branch','Office')
    department_id=fields.Many2one('hr.department', string='Department/Division', track_visibility='onchange', ondelete="restrict")


    @api.multi
    def copy_data(self, default=None):
        default = default or {}
        default.update({
            'state':'New',
            'invoiced':False,
            'invoice_ids':[],
            'remaining_hours':0.00,
            'billed_hours':0.00,
            'hours_spent':0.00
        })
        return super(AssignmentWise, self).copy_data(default)

    # _defaults = {
    # 	'state':'New',
    # 	'type':lambda s, cr, uid, c: c.has_key('type') and c['type'] or False,
    # }

    @api.multi
    def update_assignment_hours(self):
        for line in self:
            if line.hours_spent>0:
                line.remaining_hours = line.remaining_hours + line.hours_spent
        return True

    @api.multi
    def invoice_task(self):
        if not self._context:
            context = {}
        for line in self:
            partner_id = line.case_id.client_id.id
            p = self.env['res.partner'].browse(partner_id)
            acc_id = p.property_account_receivable.id
            context.update({'type':'out_invoice'})
            pettyids = self.env['account.account'].search([('name','=','PETTYCASH')])
            pettycash_acc_id = False
            if pettyids and len(pettyids) >0:
                pettycash_acc_id = pettyids[0]
            product_id=False
            prod_acc_id = False

            diff = line.hours_spent - (line.billed_hours or 0.0)
            diff_hours = (line.billed_hours or 0.0) + diff
            if line.name.name.product_id:
                product_id = line.name.name.product_id.id

                if line.name.name.product_id.property_account_income:
                    prod_acc_id = line.name.name.product_id.property_account_income.id
            inv_id = self.env['account.invoice'].create({'partner_id':partner_id,'account_id':acc_id,'invoice_line':[(0, 0, {'product_id':product_id,'name': (line.description and line.description or 'Professional Charges'), 'quantity':diff,'price_unit':line.amount,'type':'out_invoice','account_id':prod_acc_id}),(0, 0, {'product_id':False,'name': 'Out of Pocket Expenses', 'quantity':1,'price_unit':line.out_of_pocket_amount,'type':'out_invoice','account_id':pettycash_acc_id})]},context)
            # self.write([line.id], {'invoiced':True,'billed_hours':(line.type=='hour_wise' and diff_hours or 0),'invoice_ids':[(0, 0, {'assignment_wise_id':line.id,'name': inv_id,'hours':(line.type=='hour_wise' and diff or 0)})]})
            line.write({'invoiced':True,'billed_hours':(line.type=='hour_wise' and diff_hours or 0),'invoice_ids':[(0, 0, {'assignment_wise_id':line.id,'name': inv_id,'hours':(line.type=='hour_wise' and diff or 0)})]})
        return True

    @api.model
    def create(self, vals):
        # if 'amount' in vals and vals['amount']<=0:
        #     raise ValidationError(_('Amount is missing for a Hourly Stages.'))
        # if 'hours_spent' in vals and vals['hours_spent'] <= 0:
        #     raise ValidationError(_('Hours Spent is missing for a Hourly Stages.'))
        vals = self.update_related_task_for_cost_Details(vals)
        if vals.get('name') and isinstance(vals.get('name'), int):
            vals['name']=vals.get('name')
        else:
            if vals.get('name'):
                vals['name']=vals.get('name').id

        retvals = super(AssignmentWise, self).create(vals)
        return retvals

    @api.multi
    def update_related_task_for_cost_Details(self, vals):
        if 'case_fixed_id' in vals and vals['case_fixed_id']:
            retids = self.env['case.tasks.line'].search([('case_id','=',vals['case_fixed_id']),('id','=',vals['name'])])
            if not retids and vals['name']:
                line = self.env['case.tasks.line'].browse(vals['name'])
                serids = self.env['case.tasks.line'].search([('case_id','=',vals['case_fixed_id']),('name','=',line.name.id)])
                if len(serids):
                    vals['name'] = serids[0]

        if 'case_id' in vals and vals['case_id'] and 'task_new_id' in vals and vals['task_new_id']:
            task_id=vals['task_new_id']
            # task = self.env['case.tasks.line'].browse(task_id.id)

            retids = self.search([('case_fixed_id','=',task_id.case_id.id), ('name', '!=', task_id.id)])
            if retids:
                for line in retids:
                    if line.name.case_id.id != task_id.case_id.id and line.name.name.id == task_id.name.id:
                        # self.write([line.id],{'name':task.id})
                        line.write({'name':task_id.id})
        return vals

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.invoiced:
                raise UserError(_('You cannot delete an Invoiced Line!'))
                return False
        return super(AssignmentWise, self).unlink()

AssignmentWise()


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('particular_invoice_line_ids')
    def _particular_amount_all(self):
        for invoice in self:
            total = 0
            for line in invoice.particular_invoice_line_ids:
                total += line.price_unit
            invoice.particular_amount_untaxed = total

    # @api.multi
    # def _get_invoice_line(self):
    #     result = {}
    #     for line in self.env['particular.account.invoice.line'].browse(cr, uid, ids, context=context):
    #         result[line.invoice_id.id] = True
    #     return result.keys()


    account_id=fields.Many2one('account.account', 'Account', required=False, readonly=True, states={'draft':[('readonly',False)]}, help="The partner account used for this invoice.")
    office_id= fields.Many2one('hr.office', 'Office')
    ho_branch_id=fields.Many2one('ho.branch',string='HO Branch')
    #Add particular invoice ilne # Sanal Davis # 27/5/15
    particular_invoice_line_ids= fields.One2many('particular.account.invoice.line', 'invoice_id', 'Particular Invoice Lines', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)],'sent_for_validate':[('readonly',False)],'validation_reject':[('readonly',False)]})
    particular_amount_untaxed=fields.Float(compute='_particular_amount_all', string='Total')
    case_id=fields.Many2one('case.sheet','Case Sheet')


    @api.model
    def create(self, vals):
        hr_employee_pool = self.env['hr.employee']
        employee_id = hr_employee_pool.search([('user_id', '=', self.env.user.id)],limit=1)
        if vals and employee_id:
            if vals.get('office_id', False):
                vals['office_id'] = employee_id.office_id.id
            if vals.get('ho_branch_id', False):
                vals['ho_branch_id'] = employee_id.ho_branch_id.id
        inv =  super(AccountInvoice, self).create(vals)
        return inv
    
    @api.multi
    def write(self,vals):
        order =  super(AccountInvoice, self).write(vals)
        if type in ('out_invoice','out_refund'):
            if self.amount_untaxed != self.particular_amount_untaxed:
                raise UserError(_('Total Amount in Particulars is NOT EQUAL to Total Amount!'))
        return order
    
    @api.multi
    def unlink(self):
        for obj in self:
            if obj.case_id:
                for line in obj.case_id.associate_payment_lines:
                    if line.invoice_id and line.invoice_id.id == obj.id:
                        self.env['associate.payment'].write([line.id], {'invoiced':False,'invoice_id':False})
        return super(AccountInvoice, self).unlink()

    @api.multi
    def action_cancel(self):
        for obj in self:
            if obj.case_id:
                case_sheet = self.env['case.sheet'].browse(obj.case_id.id)
                for line in case_sheet.associate_payment_lines:
                    if line.invoice_id and line.invoice_id.id == obj.id:
                        self.env['associate.payment'].write([line.id], {'invoiced':False, 'invoice_id':False})
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def set_to_draft_inv(self):
        self.write({'state':'draft'})
    @api.multi
    def action_invoice_open(self):
        context = self._context.copy() or {}
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice_obj in self:
            if invoice_obj.case_id:
                assert len(invoice_obj) == 1, 'This option should only be used for a single id at a time.'
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('legal_e', 'email_template_validate_invoice')[1]
                except ValueError:
                    template_id = False
                try:
                    compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
                except ValueError:
                    compose_form_id = False
                context.update({
                    'default_model': 'account.invoice',
                    'default_res_id': invoice_obj.id,
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                    'mark_invoice_as_sent': True,
                    })
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': context,
                    }
        return res

AccountInvoice()

#Starting #create new model particular_account_invoice_line # Sanal Davis # 27/5/15
class ParticularAccountInvoiceLine(models.Model):
    _name = 'particular.account.invoice.line'
    _description = 'Paricular account line for a account line creation'

    name= fields.Text('Description', required=True)
    price_unit= fields.Float('Price')
    invoice_id=fields.Many2one('account.invoice', 'Invoice Reference', ondelete='cascade')

ParticularAccountInvoiceLine()
# Ending


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    @api.multi
    def unlink(self):
        if self.invoice_id.case_id:
            other_exp_id = self.env['other.expenses'].search([('case_id', '=', self.invoice_id.case_id.id), ('name', '=', self.description),('invoiced', '=', True)])
            if other_exp_id:
                other_exp_id.write({'invoiced':False})
        return super(AccountInvoiceLine, self).unlink()


    account_id=fields.Many2one('account.account', 'Account', required=False,  help="The income or expense account related to the selected product.")
    #Add Office in account_invoice_line
    office_id=fields.Many2one('ho.branch', 'Office')
    department_id = fields.Many2one('hr.department', string='Department/Division')
    description = fields.Text(string='Description')

    @api.multi
    def write(self, vals):
        if vals and vals.get('price_unit'):
            other_ex_id = self.env['other.expenses'].search([('case_id', '=', self.invoice_id.case_id.id),
                                                             ('billable', '=', 'bill'), ('name', '=', self.name)])
            if other_ex_id:
                # other_ex_id.write({'amount': vals['price_unit']})
                other_ex_id.write({'billed_amount': vals['price_unit']})
            else:
                fixed_price_id = self.env['fixed.price.stages'].search([('case_id', '=', self.invoice_id.case_id.id),
                                                                        ('invoiced', '=', True), ('description', '=', self.description)])
                if fixed_price_id:
                    fixed_price_id.write({'amount': vals['price_unit']})
        if vals and vals.get('office_id'):
            fixed_price_stage_id = self.env['fixed.price.stages'].search([('case_id', '=', self.invoice_id.case_id.id),
                                                                          ('invoiced', '=', True), ('description', '=', self.description)])
            if fixed_price_stage_id:
                fixed_price_stage_id.write({'office_id': vals['office_id']})
        if vals and vals.get('department_id'):
            fixed_price_stage_id = self.env['fixed.price.stages'].search([('case_id', '=', self.invoice_id.case_id.id),
                                                                          ('invoiced', '=', True), ('description', '=', self.description)])
            if fixed_price_stage_id:
                fixed_price_stage_id.write({'department_id': vals['department_id']})
        order = super(AccountInvoiceLine, self).write(vals)
        return order


class TaskActivityLine(models.Model):
    _name = 'task.activity.line'

    task_id= fields.Many2one('case.task.line', 'Activity Assignment Reference')
    name= fields.Char('Next Activity', required=True)
    action_date= fields.Datetime('Next Action Date',required=True)
    completion_date= fields.Date('Completion Date')
    state= fields.Selection([('new','New'),('inprogress','InProgress'),('done','Completed')],'Status', default='new')

    # _defaults = {
    # 	'state':'new',
    #
    # }
TaskActivityLine()


class CourtProceedingsStage(models.Model):
    _name = 'court.proceedings.stage'
    _description = 'Court Proceedings Stage'
    _order = 'sequence'

    name= fields.Char('Name', required=True)
    sequence=fields.Integer('Sequence', required=True)


class CourtProceedings(models.Model):
    _name = 'court.proceedings'
    _rec_name = 'case_id'
    _order = 'proceed_date asc'
    _inherit = ['mail.thread']

    @api.model
    def get_proceed_date(self):
        proceed_date = time.strftime('%Y-%m-%d')
        if 'default_case_id' in self._context and self._context['default_case_id']:
            ids = self.search([('case_id','=',self._context['default_case_id'])],order='id desc',limit=1)
            if ids:
                proceed_date = ids.next_proceed_date 
            else:
                proceed_date = time.strftime('%Y-%m-%d')
        return proceed_date

    @api.model
    def _check_next_proceed_date(self):
        if self._context is None:
            context = {}
        obj = self
        if obj.proceed_date and obj.next_proceed_date:
            if (datetime.strptime(obj.next_proceed_date, '%Y-%m-%d').days-datetime.strptime(obj.proceed_date, '%Y-%m-%d')).days <= 0:
                return False
        return True

    @api.multi
    def check_proceed_date(self):
        case = []
        proceed_ids =  self.search([])
        for obj in proceed_ids:
            proceed_ids1 = self.search([('proceed_date', '=', obj.proceed_date), ('case_id', '=', obj.case_id.id), ('id', '!=', obj.id)])
            if proceed_ids1:
                case.append(obj.case_id.name)
        case = list(set(case))
        return True

    @api.multi
    def _check_proceed_date(self):
        for obj in self:
            proceed_ids = self.env['court.proceedings'].search([('proceed_date', '=', obj.proceed_date), ('case_id', '=', obj.case_id.id), ('id', '!=', obj.id)])
            if proceed_ids:
                return False
        return True

    @api.multi
    def _get_order(self):
        result = {}
        for line in self:
        # for line in self.env['case.sheet'].browse():
            for court in line.court_proceedings:
                result[court.id] = True
        return result.keys()

    @api.multi
    def _get_location(self):
        result = {}
        for line in self:
        # for line in self.env['case.sheet'].browse():
            for court in line.court_proceedings:
                result[court.id] = line.ho_branch_id.id
        return result.keys()

    @api.multi
    def _get_case_name(self):
        result = {}
        for line in self:
        # for line in self.env['case.sheet'].browse():
            for court in line.court_proceedings:
                result[court.id] = line.name
        return result.keys()

    @api.multi
    def run_scheduler_mail_remind_proceed(self):
        mailids = []
        self.env.cr.execute('select current_date')
        current_date = self.env.cr.fetchone()[0]
        searids = self.search([('case_id.state','in',('new','inprogress')),('next_proceed_date','=',current_date)])
        for line in searids:
            #Mail To Assignee
            mail_temp_id = self.env['mail.template'].search([('name','=','Court Proceedings Reminder for Assignee')])
            temp_obj = self.env['mail.template'].browse(mail_temp_id[0])
            if line.case_id and line.case_id.assignee_id and line.case_id.assignee_id.work_email:
                self.env['mail.template'].send_mail(temp_obj.id, line.id, force_send=True)

            if line.case_id and line.case_id.project_id:
                team_email_to = False
                team_email_to = ', '.join([member.partner_id.email if member.partner_id.email else '' for member in line.case_id.project_id.members])

                if team_email_to:
                    if line.case_id.assignee_id.work_email:
                        team_email_to=team_email_to.replace(line.case_id.assignee_id.work_email,'')
                    self._context['email_to'] = team_email_to
                    self.env['mail.template'].send_mail(temp_obj.id, line.id, force_send=True)

            #Mail to Other Associates
            asso_mail_temp_id = self.env['mail.template'].search([('name','=','Court Proceedings Reminder for Other Associate')])
            asso_temp_obj = self.env['mail.template'].browse(asso_mail_temp_id[0])
            email_to = ', '.join([associate.name.email if associate.name.email else '' for associate in line.case_id.other_assignee_ids])
            for associate in line.case_id.other_assignee_ids:
                if associate.name.email:
                    mailids.append(associate.name.email)
            if len(mailids):
                self._context['email_to'] = email_to
                self.env['mail.template'].send_mail(asso_temp_obj.id, line.id, force_send=True)
        return True

    @api.multi
    def _parties_desc(self):
        res = {}
        for pro in self:
            parties_name = ''
            if pro.case_id:
                for line in pro.case_id.first_parties:
                    parties_name +=  "'" +line.name + "'"
                    break
                if parties_name:
                    for line in pro.case_id.opp_parties:
                        parties_name +=  '     Vs      ' + "'" + line.name + "'"
                        break
            res[pro.id] = parties_name
        return res

    # Generate sequence of seq_no
    # @api.depends('case_id')
    @api.onchange('case_id')
    def _compute_get_number(self):
        for case in self.mapped('case_id'):
            section_no = 1
            for line in case.court_proceedings:
                line.write({'seq_no': section_no})
                line.seq_no = section_no
                section_no += 1

    @api.one
    @api.depends('start_time', 'end_time')
    def _compute_no_of_hours(self):
        if self.start_time and self.end_time:
            start_time1 = datetime.strptime(str(self.start_time), '%Y-%m-%d %H:%M:%S')
            end_time1 = datetime.strptime(str(self.end_time), '%Y-%m-%d %H:%M:%S')
            time_difference = end_time1 - start_time1
            total_hours = float(time_difference.days) * 24 + (float(time_difference.seconds) / 3600)
            self.no_of_hours = total_hours

    @api.constrains('start_time', 'end_time')
    def _check_start_end_time_validate(self):
        if self.start_time > self.end_time:
            raise ValidationError(_('End Time cannot be set before Start Time.'))

    case_id= fields.Many2one('case.sheet', 'File Number')
    name=fields.Text('Court Process', required=True, track_visibility='onchange')
    proceed_date= fields.Date('Proceed Date',required=True, track_visibility='onchange', default=lambda s: s.get_proceed_date())
    flg_next_date=fields.Boolean('Next Date?', track_visibility='onchange', default=True)
    next_proceed_date=fields.Date('Next Proceed Date', track_visibility='onchange', default=lambda *a: False)
    client_id = fields.Many2one('res.partner', related='case_id.client_id', string='Client', store=True)
    tasks_lines=fields.One2many('case.tasks.line',related='case_id.tasks_lines',string='Assignee Tasks')
    associate_tasks_lines=fields.One2many('associate.tasks.line',related='case_id.associate_tasks_lines',  string='Associate Tasks')
    client_tasks_lines= fields.One2many('client.tasks.line',related='case_id.client_tasks_lines',string='Client Tasks')
    court_proceedings=fields.One2many('court.proceedings',related='case_id.court_proceedings', string='Proceedings History')
    billable=fields.Selection([('bill','Billable'),('nobill','Non-Billable')],'Billable', track_visibility='onchange')
    effective=fields.Selection([('effective','Effective'),('noeffective','Non-Effective')],'Effective', track_visibility='onchange')
    invoiced=fields.Boolean('Invoiced ?', track_visibility='onchange')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    no_of_hours=fields.Float(compute='_compute_no_of_hours', string='No Of Hours', store=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user.id)
    ho_branch_id = fields.Many2one('ho.branch', related='case_id.ho_branch_id', string='Location', store=True)
    file_number = fields.Char(related='case_id.name', string='File Number', store=True)
    old_id=fields.Many2one('court.proceedings','Old ID')
    parties_desc= fields.Char(compute='_parties_desc', string='Parties')
    court_id=fields.Many2one('court.master',related='case_id.court_id', string='Court')
    stage_id= fields.Many2one('court.proceedings.stage', 'Stage', track_visibility='onchange')
    account_analytic_line_id= fields.Many2one('account.analytic.line', 'Time Sheet', track_visibility='onchange')
    time_sheet_ids= fields.One2many('hr.analytic.timesheet', 'court_proceed_id', 'Timesheet Activities')
    date_missing= fields.Boolean('Date Missing')
    checked= fields.Boolean('Checked')
    closed= fields.Boolean('Closed')
    not_fully_billed= fields.Boolean('Not Fully Billed')
    seq_no = fields.Integer(string='Seq No', store=True)
    csm_task_desription = fields.Char('Desription of CSM Task')
    cp_effective_hearing_cost = fields.Float(string='Effective Hearing Cost')
    is_limit_exceed = fields.Boolean('Limit', default=False)

#    _constraints = [
#        (_check_proceed_date, 'You can not have 2 proceedings that overlaps on same day!', ['proceed_date'])
#    ]

    @api.onchange('seq_no', 'case_id')
    def _onchange_seq_id_check_hearing(self):
        if self.seq_no == (self.case_id.limit_on_hearing - 2):
            message = _('You have only 2 court hearing left. Please connect client for charges of future hearings.')
            warning_mess = {
                'title': _('Limit on Hearing!'),
                'message': message
            }
            return {'warning': warning_mess}
        if self.seq_no > self.case_id.limit_on_hearing:
            self.is_limit_exceed = True
        else:
            self.is_limit_exceed = False
        if self.case_id.hearing_type == 'hearing_wise':
            self.billable = 'bill'

    @api.onchange('billable', 'effective')
    def _onchange_billable_effective(self):
        if self.seq_no > self.case_id.limit_on_hearing:
            if self.billable == 'bill' and self.effective == 'effective':
                self.cp_effective_hearing_cost = self.case_id.effective_court_proceed_amount

    @api.multi
    def action_create_cp_task_csm(self):
        if self.csm_task_desription:
            tm_id = self.env['task.master'].search([('name', '=', self.csm_task_desription)])
            if tm_id:
                self.env['case.tasks.line'].create({
                    'slno': len(self.case_id.tasks_lines) + 1,
                    'name': tm_id.id,
                    'assign_to': self.case_id.client_service_executive_id.id,
                    'start_date': fields.Date.today(),
                    'days': 1,
                    'planned_completion_date': fields.Date.today(),
                    'case_id': self.case_id.id,
                })

    @api.multi
    def check_issues(self):
        proceeding_ids =  self.search([('checked', '=', True),('case_id.state', 'not in', ('new','done','cancel','transfer', 'hold'))])
        case_ids = [proce_obj.case_id.id for proce_obj in proceeding_ids]
        for case_id in case_ids:
            proc_ids =  self.search([('case_id', '=', case_id),('next_proceed_date', '!=', False)], order='next_proceed_date desc')
            if proc_ids:
                proceed_obj = proc_ids[0]
                res_ids = self.search([('case_id', '=', case_id),('proceed_date', '=', proceed_obj.next_proceed_date)])
                if not res_ids:
                    if proceed_obj.next_proceed_date < time.strftime('%Y-%m-%d') and not proceed_obj.date_missing:
                        # self.write([proceed_obj.id], {'checked': False, 'date_missing': False})
                        proceed_obj.write({'checked': False, 'date_missing': False})
                else:
                    prod_obj = res_ids[0]
                    # prod_obj = self.browse(res_ids[0])
                    if not prod_obj.next_proceed_date and prod_obj.stage_id.id == 53:
                        # self.write([proceed_obj.id], {'checked': False, 'date_missing': False})
                        proceed_obj.write({'checked': False, 'date_missing': False})
        return True

    @api.multi
    def check_fully_billed(self):
        invoice_pool = self.env['account.invoice']
        proceeding_ids =  self.search([('date_missing', '=', False),('case_id.state', 'not in', ('new','done','cancel','transfer', 'hold'))])
        case_ids = [proce_obj.case_id for proce_obj in proceeding_ids if proce_obj.case_id.billed_amount > proce_obj.case_id.received_amount]
        for case_id in case_ids:
            payment_due = False
            invoice_ids = invoice_pool.search([('case_id', '=', case_id).id, ('state', '=', 'open')], order='date_invoice asc',limit=1)
            if invoice_ids:
                invoice_obj = invoice_ids
                due_date = (datetime.strptime(invoice_obj.date_invoice, '%Y-%m-%d') + timedelta(days=60)).strftime('%Y-%m-%d')
                if due_date <= time.strftime('%Y-%m-%d'):
                    payment_due = True
            if payment_due:
                proc_ids =  self.search([('case_id', '=', case_id.id),('next_proceed_date', '!=', False),('name', '!=', 'Missing Dates(System generated message)')], order='next_proceed_date desc', limit=1)
                if proc_ids:
                    proceed_obj = proc_ids
                    res_ids = self.search([('case_id', '=', case_id.id),('proceed_date', '=', proceed_obj.next_proceed_date)])
                    if not res_ids:
                        if proceed_obj.next_proceed_date > time.strftime('%Y-%m-%d'):
                            # self.write([proceed_obj.id], {'not_fully_billed': True})
                            proceed_obj.write({'not_fully_billed': True})
                    proc_ids.remove(proc_ids)
                    if proc_ids:
                        self.env.cr.execute('update court_proceedings set not_fully_billed =False where id in %s',(tuple(proc_ids),))


        proceeding_ids = [proce_obj.id for proce_obj in proceeding_ids if proce_obj.case_id.billed_amount == proce_obj.case_id.received_amount]
        proceeding_ids = list(set(proceeding_ids))
        # self.write(proceeding_ids, {'not_fully_billed': False})
        proceeding_ids.write({'not_fully_billed': False})
        return True

    @api.multi
    def missing_date_scheduler(self):
        proceeding_ids =  self.search([('case_id.work_type','!=', 'non_litigation'),('case_id.state', 'not in', ('new','done','cancel','transfer', 'hold')),('case_id.division_id.exclude_dashboard', '=', False)])
        case_ids = [proce_obj.case_id for proce_obj in proceeding_ids]
        for case_id in case_ids:
            proc_ids =  self.search([('case_id', '=', case_id),('next_proceed_date', '!=', False)], order='next_proceed_date desc')
            if proc_ids:
                proceed_obj = proc_ids
                res_ids = self.search([('case_id', '=', case_id),('proceed_date', '=', proceed_obj.next_proceed_date)],limit=1)
                if not res_ids:
                    if proceed_obj.next_proceed_date < time.strftime('%Y-%m-%d'):
                        # self.write([proceed_obj.id], {'date_missing': True, 'checked': True})
                        proceed_obj.write({'date_missing': True, 'checked': True})
            miss_procee_ids =  self.search([('case_id', '=', case_id),('next_proceed_date', '=', False),('flg_next_date', '=', False)])
            for procee_obj in miss_procee_ids:
                date = (datetime.strptime(procee_obj.proceed_date, '%Y-%m-%d') + timedelta(days=90)).strftime('%Y-%m-%d')
                if date < time.strftime('%Y-%m-%d'):
                    # self.write([procee_obj.id], {'date_missing': True, 'checked': True})
                    proceed_obj.write({'date_missing': True, 'checked': True})
            miss_ids =  self.search([('case_id', '=', case_id), ('next_proceed_date', '=', False), ('flg_next_date', '=', True)])
            for procee_obj in miss_ids:
                if procee_obj.proceed_date < time.strftime('%Y-%m-%d'):
                    # self.write([procee_obj.id], {'date_missing': True, 'checked': True})
                    proceed_obj.write({'date_missing': True, 'checked': True})
            miss_date_ids =  self.search([('case_id', '=', case_id),('date_missing', '=', True)])
            for procee_obj in miss_date_ids:
                pro_ids = self.search([('case_id', '=', case_id),('proceed_date', '=', procee_obj.next_proceed_date)])
                if pro_ids:
                    # self.write([procee_obj.id], {'date_missing': False, 'checked': True})
                    proceed_obj.write({'date_missing': False, 'checked': True})
        casesheet_ids = self.env['case.sheet'].search([('work_type','!=', 'non_litigation'), ('court_id','!=', False), ('court_proceedings', '=', False),('state', 'not in', ('draft','done','cancel','transfer', 'hold')),('division_id.exclude_dashboard', '=', False)])
        case_ids = [case_obj for case_obj in casesheet_ids if (datetime.strptime(case_obj.date, '%Y-%m-%d') + timedelta(days=180)).strftime('%Y-%m-%d') < time.strftime('%Y-%m-%d')]
        for case_id in case_ids:
            vals = {
                'case_id': case_id,
                'proceed_date': time.strftime('%Y-%m-%d'),
                'name': 'Missing Dates(System generated message)',
                'checked': True,
                'date_missing': True,
                }
            self.create(vals)
        proceed_stage_id = self.env['res.users'].browse(self.env.user.id).company_id.proceed_stage_id.id
        proceeding_ids =  self.search(['|',('case_id.state', 'in', ('new','done','cancel','transfer', 'hold')),('stage_id', '=', proceed_stage_id)])
        # self.write(proceeding_ids, {'checked': True, 'date_missing': False})
        proceeding_ids.write({'checked': True, 'date_missing': False})
        return True

    @api.multi
    def search(self,args, offset=0, limit=None, order=None, context=None, count=False):
        if self._context is None:
            context = {}
        if self._context.get('order_by_next_proceed_date', False):
            order = 'next_proceed_date asc'
        return super(CourtProceedings, self).search(args,offset=offset, limit=limit, order=order, count=count)

    @api.multi
    def button_refresh(self):
        return True

    @api.onchange('case_id')
    def onchange_case_id(self):
        if self._context is None:
            context = {}
        context=self.env.context.copy()
        res = {}
        if self.case_id:
            # context['case_id'] = self.case_id
            context.update({'case_id':self.case_id.id})
            res['proceed_date'] = self.get_proceed_date()
        return {'value':res}

    @api.onchange('case_id')
    def onchange_caseid(self):
        res={}
        return {'value':res}

    @api.model
    def default_get(self, fields_list):
        if not self._context:
            context = {}
            
        res = super(CourtProceedings, self).default_get(fields_list)
        if 'default_case_id' in self._context:
            proceed_date = time.strftime('%Y-%m-%d')
            proceed_id = self.search([('case_id','=',self._context['default_case_id'])],limit=1, order='id desc')
            if proceed_id:
                proceed_date = proceed_id[0].next_proceed_date
            res.update({'proceed_date':proceed_date})
        return res

    @api.onchange('flg_next_date')
    def onchange_flg_next_date(self):
        res={}
        res['next_proceed_date'] = False
        return {'value':res}

    @api.model
    def create(self, vals):
        if not vals.get('flg_next_date', False):
            vals['next_proceed_date'] = False

        if vals.get('proceed_date', False):
            ids = self.search([('case_id','=',vals['case_id'])],order='id desc',limit=1)
            proceed_date = False
            for rec in ids:
                proceed_date = rec.next_proceed_date
            if proceed_date and vals['proceed_date'] != proceed_date:
                vals['proceed_date'] = proceed_date

        if vals.get('case_id', False):
            proc_ids =  self.search([('case_id', '=', vals['case_id']),('next_proceed_date', '!=', False)], order='next_proceed_date desc')
            if proc_ids:
                proceed_obj = proc_ids[0]
                if proceed_obj.next_proceed_date == vals['proceed_date'] and proceed_obj.date_missing:
                    # self.write([proceed_obj.id], {'date_missing': False})
                    proceed_obj.write({'date_missing': False})

        if vals.get('stage_id', False):
            proceed_stage_id = self.env['res.users'].browse(self.env.user.id).company_id.proceed_stage_id.id
            if vals['stage_id'] == proceed_stage_id:
                vals.update({'date_missing': False, 'checked': True, 'closed': True})
            else:
                vals.update({'date_missing': False, 'checked': False, 'closed': False})

        retvals = super(CourtProceedings, self).create(vals)
        # if retvals and retvals.billable=='bill' and retvals.no_of_hours>0 and retvals.case_id.project_id:
        if retvals.case_id.bill_type == 'assignment_wise' and retvals.billable == 'bill':
            # if retvals.case_hourly_id.bill_type == 'assignment_wise' and retvals.effective == 'effective':
            #     hourly_amount = retvals.case_hourly_id.effective_court_proceed_amount
            # else:
            #     hourly_amount = retvals.case_hourly_id.non_effective_court_proceed_amount
            self.env['assignment.wise'].create({
                'case_hourly_id': retvals.case_id.id,
                'description': 'Upon hearing (' + str(retvals.effective or '') + ')',
                'amount': retvals.case_id.bill_type == 'assignment_wise' and retvals.effective == 'effective' and retvals.case_id.effective_court_proceed_amount or retvals.case_id.non_effective_court_proceed_amount,
                'hours_spent': 1.0,
                'office_id': retvals.case_id.ho_branch_id.id,
            })
        if retvals and retvals.no_of_hours > 0.0 and retvals.case_id.project_id:
#            start_date = fields.Date.from_string(retvals.start_time)
#            end_date = fields.Date.from_string(retvals.end_time)
#            if start_date == end_date:
            emp_id = self.env['hr.employee'].search([('user_id','=',retvals.user_id.id)])
            account_analytic_line_id=self.env['account.analytic.line'].create({
                'date':retvals.proceed_date,
                'project_id':retvals.case_id.project_id.id,
                'name':retvals.name,
                'start_time':retvals.start_time,
                'end_time':retvals.end_time,
                'unit_amount':retvals.no_of_hours,
                'employee_id':emp_id.id
            })
            if account_analytic_line_id:
                retvals.account_analytic_line_id=account_analytic_line_id.id
#            else:
#                raise UserError(_('You only fill up today timesheet!'))
        return retvals

    @api.multi
    def write(self, vals):
        if 'flg_next_date' in vals:
            if not vals['flg_next_date']:
                vals['next_proceed_date'] = False
        if vals.get('next_proceed_date', False) or vals.get('proceed_date', False) or vals.get('name', False) or vals.get('case_id', False):
            vals.update({'date_missing': False, 'checked': False, 'closed': False})
        if vals.get('proceed_date', False):
            proceed_date = False
            for rec in self:
                proceed_ids = self.search([('case_id','=',rec.case_id.id),('id', '!=', rec.id)],order='id desc',limit=1)
                for procee_obj in proceed_ids:
                    proceed_date = procee_obj.next_proceed_date
            if proceed_date and vals['proceed_date'] != proceed_date:
                vals['proceed_date'] = proceed_date

        if vals.get('stage_id', False):
            proceed_stage_id = self.env['res.users'].browse(self.env.user.id).company_id.proceed_stage_id.id
            if vals['stage_id'] == proceed_stage_id:
                vals.update({'date_missing': False, 'checked': True, 'closed': True})
            else:
                vals.update({'date_missing': False, 'checked': False, 'closed': False})
        retvals = super(CourtProceedings, self).write(vals)
#        for record in self:
#	    if record.account_analytic_line_id:
 #               record.account_analytic_line_id.name=record.name
  #              record.account_analytic_line_id.date=record.proceed_date
   #             record.account_analytic_line_id.project_id=record.case_id.project_id.id
    #            record.account_analytic_line_id.unit_amount=record.no_of_hours
        if self.account_analytic_line_id:
            self.account_analytic_line_id.name=self.name
            self.account_analytic_line_id.date=self.proceed_date
            self.account_analytic_line_id.project_id=self.case_id.project_id.id
            self.account_analytic_line_id.unit_amount=self.no_of_hours
        # if self.account_analytic_line_id:
        #     self.account_analytic_line_id.name=self.name
        #     self.account_analytic_line_id.date=self.proceed_date
        #     self.account_analytic_line_id.project_id=self.case_id.project_id.id
        #     self.account_analytic_line_id.unit_amount=self.no_of_hours
        return retvals

    @api.multi
    def unlink(self):
        for obj in self:
            proceed_ids = self.search([('case_id', '=', obj.case_id.id),('id', '!=', self.ids[0])])
            # self.write(proceed_ids, {'checked': False})
            proceed_ids.write({'checked': False})
        return super(CourtProceedings, self).unlink()

    @api.multi
    def copy_data(self, default=None):
        default = default or {}
        if self._context is None:
            context = {}
        case_id = self.browse(self.ids).case_id.id
        context['case_id'] = case_id

        default.update({
#             'next_proceed_date':False,
            'checked': False,
            'date_missing': False,
            'case_id' : False,
#             'proceed_date': self.get_proceed_date(cr, uid, context=context)
            })
        return super(CourtProceedings, self).copy_data(default)


class FirstPartiesDetails(models.Model):
    _name = 'first.parties.details'
    _order = 'sl_no'

    sl_no= fields.Integer('Sl no')
    party_id= fields.Many2one('case.sheet', 'First Parties Reference')
    name= fields.Char('Party Name', required=True)
    type= fields.Selection([('plaintiff','PLAINTIFF'),('petitioner','PETITIONER'),('applicant','APPLICANT'),('appellant','APPELLANT'),('caveator','CAVEATOR'),('intervener','INTERVENER'),('claimaints','CLAIMANTS')],'Type',required=True)

    @api.multi
    def get_selection_value(self, field, field_id):
        res = ''
        if not field_id:
            return res
        fields_get_result = self.fields_get([field,])
        if fields_get_result:
            selection = fields_get_result[field]['selection']
            if selection:
                for key_value in selection:
                    if field_id == key_value[0]:
                        res = key_value[1]
        return res
FirstPartiesDetails()

class OppPartiesDetails(models.Model):
    _name = 'opp.parties.details'
    _order = 'sl_no'

    sl_no= fields.Integer('Sl no')
    party_id= fields.Many2one('case.sheet', 'Opposite Parties Reference')
    name= fields.Char('Party Name')
    type=fields.Selection([('defendant','DEFENDANT'),('respondant','RESPONDENT'),('oopparty','OPP PARTY'),('accused','ACCUSED'),('caveatee','CAVEATEE')],'Type')

    @api.multi
    def get_selection_value(self, field, field_id):
        res = ''
        if not field_id:
            return res
        fields_get_result = self.fields_get([field,])
        if fields_get_result:
            selection = fields_get_result[field]['selection']
            if selection:
                for key_value in selection:
                    if field_id == key_value[0]:
                        res = key_value[1]
        return res

OppPartiesDetails()


class OppParties(models.Model):
    _name = 'opp.parties'

    name=fields.Char('Name', required=True)
    email= fields.Char('Email',size=240)
    phone= fields.Char('Phone',size=32)
    mobile= fields.Char('Mobile',size=32)

OppParties()


class FixedPriceStages(models.Model):
    _name = 'fixed.price.stages'
    _order = 'case_id desc'

    @api.multi
    def _get_invoiced_total(self):
        res = {}
        for line in self:
            total = 0.0
            if line.invoice_id:
                inv = self.env['account.invoice'].browse(line.invoice_id.id)
                total = inv.amount_total
            res[line.id] = total
        return res

    @api.multi
    def _get_invoiced_balance(self):
        res = {}
        for line in self:
            residual = 0.0
            if line.invoice_id:
                inv = self.env['account.invoice'].browse(line.invoice_id.id)
                residual = inv.residual
            res[line.id] = residual
        return res

    @api.multi
    def _get_invoiced_state(self):
        res = {}
        for line in self:
            state = False
            if line.invoice_id:
                states = {'draft':'Draft','proforma':'Pro-forma','proforma2':'Pro-forma','sent_for_validate':'Sent For Validate','validation_reject':'Validation Rejected','open':'Open','paid':'Paid','cancel':'Cancelled','sent_revised_bill':'Sent for Revised Bill','revised_bill_reject':'Revised Bill Rejected'}
#                inv = self.env['account.invoice'].browse(line.invoice_id.id)
                state = states[line.invoice_id.state]
            res[line.id] = state
        return res

    @api.multi
    def view_invoice_task(self):
        obj = self.ids[0]
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
        except ValueError as e:
            view_id = False
        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.invoice_id.id,
        }

    @api.multi
    def view_case_sheet(self):
        obj = self.ids[0]
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'case_sheet_form')
        except ValueError as e:
            view_id = False
        return {
            'name': _('Case Sheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'case.sheet',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.case_id.id,
        }

    case_id= fields.Many2one('case.sheet', 'File Number')
    fixed_price= fields.Float(related='case_id.fixed_price', string='Fixed Price')
    bill_type= fields.Selection(related='case_id.bill_type', string='Billing Type')
    casetype_id= fields.Many2one('case.master', related='case_id.casetype_id', string='Case Type')
    name=fields.Many2one('case.tasks.line','Task Related', required=True,readonly=False,)
    description=fields.Char('Description', size=1024,copy=True)
    assignee_id= fields.Many2one('hr.employee', 'Assignee', copy=False)
    percent_amount=fields.Float('Amount in %', digits=dp.get_precision('Account'))
    amount= fields.Float('Amount', digits=dp.get_precision('Account'))
    out_of_pocket_amount= fields.Float('Out of Pocket Expense')
    # 'state':fields.related('name','state',type='selection',selection=[('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Pending','Pending'),('Completed','Completed'),('Invoiced','Invoiced')],string="Status"),
    state = fields.Char(related='name.state', string='Status', default='New')
    # related = 'name.state',
    invoiced=fields.Boolean('Invoiced')
    #new field
    department_id=fields.Many2one('hr.department', string='Department/Division', track_visibility='onchange', ondelete="restrict")
    invoice_id=fields.Many2one('account.invoice', string='Invoice ID', store=True)
    inv_state= fields.Char(compute='_get_invoiced_state',string='INV Status', readonly=True)
    inv_total_amt=fields.Float(compute='_get_invoiced_total',string='Total INV Amt',readonly=True)
    inv_balance_amt=fields.Float(compute='_get_invoiced_balance',string='Balance INV Amt',readonly=True)
    old_id=fields.Many2one('fixed.price.stages','Old ID')
    office_id=fields.Many2one('ho.branch','Office') #add office field # Sanal Davis # 27/5/15

    # _defaults = {
    # 	'state':'New',
    # }

    # Starting Sanal Davis 27/5/15
    @api.onchange('name')
    def onchange_office(self):
        '''
        This function writes the office field value
        '''
        if self.name:
            office_id = self.name.office_id.id or False
        else:
            office_id = False
        return {'value': {'office_id': office_id}}

    @api.model
    def create(self, values):
        # fixed_price_stages_id = self.env['fixed.price.stages'].search([('case_id', '=', values.get('case_id', False)), ('name', '=', values.get('name', False))])
        fixed_price_stages_id = self.env['fixed.price.stages'].search(
            [('case_id', '=', values.get('case_id', False)), ('description', '=', values.get('description', False))])
        if fixed_price_stages_id:
            raise UserError(_("Task description is already exist in Fixed Price Stages!"))
        return super(FixedPriceStages, self).create(values)

    @api.multi
    def copy_data(self, default=None):
        default = default or {}
        default.update({
            'state':'New',
            'invoiced':False,
            'invoice_id':False
        })
        return super(FixedPriceStages, self).copy_data(default)

    @api.multi
    def update_related_task_for_cost_Details(self, vals):
        if 'case_id' in vals and vals['case_id'] and 'task_new_id' in vals and vals['task_new_id']:
            # task = self.env['case.tasks.line'].browse(vals['task_new_id'])
            task =vals['task_new_id']
            retids = self.search([('case_id','=',task.case_id.id),('name','!=',task.id)])
            if retids:
                for line in retids:
                    if line.name.case_id.id != task.case_id.id and line.name.name.id == task.name.id:
                        # self.write([line.id],{'name':task.id})
                        line.write({'name':task.id})
        return vals

    @api.multi
    def check_task_in_assignee_tasks(self, taskid):
        assignids = []
        for line in self._context['assignee_task_lines']:
            assignids.append(line[2]['name'])
        if taskid not in assignids:
            warning = {
                       'title': _('Error!'),
                       'message' : _('Selected Task is not Present in Assignee Tasks.')
                    }
            return {'value': {'name':False}, 'warning': warning}
        return {'value': {'name':taskid}}

    @api.multi
    def invoice_stage(self):
        if not self._context:
            context = {}
        for line in self:
            partner_id = line.case_id.client_id.id
            p = self.env['res.partner'].browse(partner_id)
            acc_id = p.property_account_receivable.id
            context.update({'type':'out_invoice'})
            pettyids = self.env['account.account'].search([('name','=','PETTYCASH')])
            pettycash_acc_id = False
            if pettyids and len(pettyids) >0:
                pettycash_acc_id = pettyids[0]
            product_id=False
            prod_acc_id = False
            if line.name.name.product_id:
                product_id = line.name.name.product_id.id
                if line.name.name.product_id.property_account_income:
                    prod_acc_id = line.name.name.product_id.property_account_income.id

            inv_id = self.env['account.invoice'].create({'partner_id':partner_id,'account_id':acc_id,'invoice_line':[(0, 0, {'product_id':product_id,'name':(line.description and line.description or 'Professional Charges'), 'quantity':1.0,'price_unit':line.amount,'type':'out_invoice','account_id':prod_acc_id}), (0, 0, {'name':'Out of Pocket Expenses', 'quantity':1.0,'price_unit':line.out_of_pocket_amount,'type':'out_invoice','account_id':pettycash_acc_id})]})
            # self.write([line.id], {'invoiced':True,'invoice_id':inv_id})
            line.write({'invoiced':True, 'invoice_id':inv_id})
        return True
#not used
#    @api.onchange('percent_amount', 'fixed_price', 'casetype_id', 'bill_type','amount')
#    def onchange_percent(self):
#        if self.case_id:
#            if self.case_id.fixed_price:
#                amount = (float(self.case_id.fixed_price)*self.percent_amount)/100
#                return {'value':{'amount':amount}}
#            else:
#                raise UserError(_('Enter the Fixed Price Amount First!'))
#        return {'value':{'amount':0,'percent_amount':0}}

    @api.onchange('amount', 'fixed_price','casetype_id', 'bill_type','percent_amount')
    def onchange_amount(self):
        for record in self:
            if record.case_id:
                if record.case_id.fixed_price>0.0:
                    record.amount=self.amount
                else:
                    raise UserError(_('Enter the Fixed Price Amount First!'))

    @api.multi
    def write(self, vals):
        if not self._context.get('case_copy', False):
            if vals.get('amount', False) or vals.get('out_of_pocket_amount', False) or vals.get('office_id', False) or vals.get('description', False) or vals.get('name', False):
                for data_obj in self:
                    if data_obj.case_id.state != 'new' and  not self.env['res.users'].has_group('legal_e.group_case_sheet_operation_manager'):
                        raise UserError(_('You are not permitted to modifie this record. Contact case sheet operations manager.'))
        res = super(FixedPriceStages, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.invoiced and obj.state == 'Completed':
                raise UserError(_('Error!'),_('You cannot delete an Invoiced Line!'))
                return False
            if obj.case_id.state != 'new' and  not self.env['res.users'].has_group('legal_e.group_case_sheet_operation_manager'):
                raise UserError(_('Warning!'), _('You are not permitted to delete this record. Contact case sheet operations manager.'))

        return super(FixedPriceStages, self).unlink()

FixedPriceStages()


class Project(models.Model):
    _inherit = 'project.project'
#    task_count = fields.Integer(compute='_compute_task_count', string="Tasks",store=True)

    @api.multi
    def set_done(self):
        if not self._context.get('case_close', False):
            for project_id in self.ids:
                sheet_ids = self.env['case.sheet'].search([('project_id', '=', project_id)])
                for sheet_id in sheet_ids:
                    state = self.env['case.sheet'].browse(sheet_id).state
                    if state == 'inprogress':
                        raise UserWarning(_('You cannot close the project!\n\n Please close the case sheet before closing the project.'))
#        res = super(Project, self).set_done()
        return True
    
    case_id=fields.Many2one('case.sheet','Case')
    members=fields.Many2many('res.users', 'project_user_rel', 'project_id', 'uid', string='Project Members')

Project()


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    state= fields.Selection(_TASK_STATE, 'Related Status', required=True, help="The status of your document is automatically changed regarding the selected stage. "
    "For example, if a stage is related to the status 'Close', when your document reaches this stage, it is automatically closed.")


ProjectTaskType()

# class project_task_history(osv.osv):
#     _inherit = 'project.task.history'
#     _columns = {
#        'state': fields.selection([('draft', 'New'), ('cancelled', 'Cancelled'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'),('hold', 'Hold')], 'Status'),
#         }
#
# project_task_history()


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _order = 'due_days desc'
    _rec_name='task_name'
    _track = {
        'state': {
            'protsk.mt_task_state': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['draft','open','pending','done','cancelled']
        },
    }

    @api.multi
    def _get_assigned_to(self):
        for line in self:
            assigned_to = False
            if line.task_for == 'employee':
                if line.assignee_id:
                    line.assigned_to = line.assignee_id.name
            if line.task_for == 'associate':
                if line.other_assignee_id:
                    line.assigned_to = line.other_assignee_id.name
            if line.task_for == 'customer':
                if line.client_id:
                    line.assigned_to = line.client_id.name
#not use
#    @api.multi
#    def _get_manager_user(self):
#        res = {}
#        for project in self:
#            manager = False
#            if project:
#                if project and project.user_id:
#                    manager = project.user_id.id
#            res[project.id] = manager
#        return res.keys()

    @api.onchange('assignee_id')
    def onchange_assignee(self):
        res = {}
        if not self.assignee_id:
            res['assignee_user_id'] = False
        else:
            emp = self.env['hr.employee'].browse(self.assignee_id)
            user_id = False
            if emp and emp.user_id:
                user_id = emp.user_id.id
            res['assignee_user_id'] = user_id
        return {'value':res}

    @api.multi
    def compute_due_days(self):
        res = {}

        for line in self:
            days = False
            if line.date_deadline:
                days = (datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d') - datetime.strptime(line.date_deadline, '%Y-%m-%d')).days
            res[line.id] = days
        return res

    @api.multi
    def _compute_due_days_string(self):
        res = {}
        searids = self.search([('state','!=','done'),'|',('today_date','=',False),('today_date','!=',time.strftime('%Y-%m-%d'))])
        for line in searids:
            days = False
            due_days_string = False
            if line.date_deadline:
                if line.state == 'done':
                    due_days_string = 'completed'
                else:
                    days = (datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d') - datetime.strptime(line.date_deadline, '%Y-%m-%d')).days
                    if days>0:
                        due_days_string = str(days) + ' days over due'
                    else:
                        due_days_string = str(abs(days)) + ' days to complete'
                    self.env.cr.execute('update project_task set due_days =%s,today_date=%s where id=%s',(days,time.strftime('%Y-%m-%d'),line.id))
                    self.env.cr.commit()
            res[line.id] = due_days_string
        return res

    @api.multi
    def run_scheduler(self):
        self.env.cr.execute('select current_date')
        current_date = self.env.cr.fetchone()[0]
        searids = self.search([('state','in', ('draft', 'open', 'pending'))])
        pending_stage_id = False
        comids = self.env['project.task.type'].search([('name','=','Pending'),('state','=','pending')],limit=1)
        if comids and len(comids):
            pending_stage_id = comids.id
        for line in searids:
            days = 0
            due_days_string = False
            state = line.stage_id.id
            sta = line.state
            if line.date_deadline:
                days = (datetime.strptime(current_date, '%Y-%m-%d') - datetime.strptime(line.date_deadline, '%Y-%m-%d')).days
                if days>0:
                    due_days_string = str(days) + ' days over due'
                    state = pending_stage_id and pending_stage_id or state
                    sta = 'pending'
                else:
                    due_days_string = str(abs(days)) + ' days to complete'
            self.env.cr.execute('update project_task set due_days =%s,due_days_string =%s,today_date=%s,stage_id=%s, state=%s where id=%s',(days,due_days_string,current_date,state,sta,line.id))
            self.env.cr.commit()
        return True

    @api.multi
    def run_scheduler_for_task_message(self):
        searids = self.env['project.task'].search([('flg_message','=',True)])
        vals = {}
        vals['remaining_hours'] = 0.0
        vals['state']='done'
        comids = self.env['project.task.type'].search([('name','=','Completed'),('state','=','done')],limit=1)
        if comids and len(comids):
            vals['stage_id']=comids.id
        vals['progress']=100
        vals['flg_message']=False
        if searids:
            searids.write(vals)
        return True

    @api.multi
    def run_scheduler_for_pending_task_message(self):
        r = []
        j = []
        search_ids = self.search([('state','=','pending')])
        user = self.env['res.users'].browse(self.env.user.id)
        for dt in self.env['project.task'].read(search_ids, ['assignee_id']):
            if dt['assignee_id']:
                r.append(dt['assignee_id'][0])
        for line in self.env['hr.employee'].browse(list(set(r))):
            srch_ids = self.search([('state','=','pending'),('assignee_id','=',line.id)])
            for self_obj in self.read(srch_ids, ['name','project_id']):
                j.append('Project : {0} ====> Task : {1}'.format(self_obj['project_id'][1],self_obj['name'][1]))
        #Mail To Assignee
            if line.user_id and line.user_id.partner_id:
                post_values =  {
                    'email_from': user.partner_id.email or False,
                    'partner_ids': [line.user_id.partner_id.id],
                    'subject': 'PENDING Tasks',
                    'body': 'Following List of Tasks Assigned for you are PENDING : \n %s.' % (j),
                    }
                subtype = 'mail.mt_comment'
                self.message_post([srch_ids[0]], type='comment', subtype=subtype, **post_values)
        return True

#use as related field
#    def _get_reg_number(self):
#        res = {}
#        for task in self:
#            case_ids = self.env['case.sheet'].search([('project_id','=',task.project_id.id)])
#            for case in case_ids:
#                task.reg_number = case.reg_number

#use as related field
#    @api.multi
#    def _get_first_parties(self, field_names):
#        for task in self:
#            firstids = []
#            first_parties
#            case_ids = self.env['case.sheet'].search([('project_id','=',task.project_id.id)])
#            for case in case_ids:
#                for first in case.first_parties:
#                    firstids.append((0,0,{'type':first.type,'name':first.name}))
#                res[task.id] = firstids

#use as related field
#    @api.multi
#    def _get_opp_parties(self, field_names):
#        res = {}
#        task = self.ids[0]
#        oppids = []
#        case_ids = self.env['case.sheet'].search([('project_id','=',task.project_id.id)])
#        for case in case_ids:
#            for opp in case.opp_parties:
#                oppids.append((0,0,{'type':opp.type,'name':opp.name}))
#            res[task.id] = oppids
#        return res

    @api.multi
    def _get_bill_amount(self):
        for task in self:
            line_ids = self.env['case.tasks.line'].search([('task_id','=',task.id)])
            if line_ids:
                bill_lines = self.env['fixed.price.stages'].search([('name','in',line_ids.ids)])
                if len(bill_lines)>0:
                    for line in bill_lines:
                        task.bill_amount = (line.amount and line.amount or 0.00)
                else:
                    task.bill_amount = 0.00

    @api.multi
    def update_project_task_user(self):
        proj_ids = self.env['project.task'].search([])
        for task in proj_ids:
            task.write({'proj_mgr_usr_id':task.project_id.user_id and task.project_id.user_id.id or False})
        return True


    task_for=fields.Selection([('employee','Assignee'),('associate','Associate'),('customer','Client')],'Task For',required=True)
    billable=fields.Boolean('Billable')
    assignee_id=fields.Many2one('hr.employee','Assigned to(Assignee)')
    other_assignee_id=fields.Many2one('res.partner','Assigned to(Associate)',domain="[('supplier','=',True)]")
    client_id=fields.Many2one('res.partner','Assigned to(Client)')
    case_id=fields.Many2one(related='project_id.case_id',string='Case')
    # 'assigned_to':fields.function(_get_assigned_to, string='Assigned to(User)', type='char',store=
    #     {'project.task': (lambda self, cr, uid, ids, c={}: ids, ['assignee_id','other_assignee_id','client_id'], 20)}),
    assigned_to=fields.Char(compute='_get_assigned_to', string='Assigned to(User)', store=True)
    #'proj_mgr_usr_id':fields.function(_get_manager_user, string='Project Manager', type='Many2one', relation='res.users', store={'project.project': (lambda self, cr, uid, ids, c={}: ids, ['user_id'], 20)}),
    # 'proj_mgr_usr_id':fields.related('project_id','user_id',type='Many2one',relation='res.users',string='project Manager',
    #     store={
    #         'project.task': (lambda self, cr, uid, ids, c={}: ids, ['project_id'], 10),
    #         'project.project': (_get_manager_user, ['user_id'], 10),
    #     }),
    proj_mgr_usr_id = fields.Many2one('res.users', related='project_id.user_id', string='Project Manager', store=True)
    task_name=fields.Many2one('task.master','Name',required=True)
    assignee_user_id= fields.Many2one('res.users','Assignee User ID')
    project_id=fields.Many2one('project.project', 'Project', ondelete='set null',track_visibility='onchange')
    due_days_string=fields.Char('Due Days')
    due_days=fields.Integer('Due Days')
    reg_number=fields.Char(related='case_id.reg_number',string='Case No.')
#    reg_number=fields.Char(compute='_get_reg_number',string='Case No.')
    first_parties= fields.One2many('first.parties.details', related='case_id.first_parties', string='First parties of the Case')
#    first_parties= fields.One2many('first.parties.details',compute='_get_first_parties', string='First parties of the Case')
    opp_parties= fields.One2many('opp.parties.details', related='case_id.opp_parties', string='Opposite parties of the Case')
#    opp_parties= fields.One2many('opp.parties.details',compute='_get_opp_parties', string='Opposite parties of the Case')
    bill_amount=fields.Float(compute='_get_bill_amount',string='Billing Amount')
    today_date=fields.Date('Last Updated Date')
    flg_message=fields.Boolean('Generate mail Message', track_visibility='always')
    state= fields.Selection( related = 'stage_id.state',store=True,
            string="Status", readonly=True,
            help='The status is set to \'Draft\', when a case is created.\
                  If the case is in progress the status is set to \'Open\'.\
                  When the case is over, the status is set to \'Done\'.\
                  If the case needs to be reviewed then the status is \
                  set to \'Pending\'.', track_visibility='always')
    # related = 'stage_id.state',
    lot_name= fields.Char('Lot Number', size=64, readonly=True)
    name = fields.Char(string='Task Title', track_visibility='always', required=False, index=True)


    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}

        if context.get('order_by_end_date', False):
            order = 'date_end desc'
#             cr.execute("select project_id from case_sheet where division_id in (select id from hr_department where exclude_dashboard=True) and active=True;")
#             project_ids= [a[0] for a in map(lambda x: x, cr.fetchall())]
#
#             cr.execute('select id from project_task where project_id in %s;',(tuple(project_ids),))
#             tasks_ids = [a[0] for a in map(lambda x: x, cr.fetchall())]
#             args += [('id','not in', tasks_ids)]
        return super(ProjectTask, self).search(args, offset, limit, order, count=count)

    @api.multi
    def name_get(self):
        res = []
        if not self.ids:
            return res
        for task_line in self:
            res.append((task_line.id,task_line.name))
        return res

    # Starting // Sanal Davis // 4-6-15
    @api.multi
    def project_task_reevaluate(self):
        '''
         Set warning for invoiced task if we press reevaluate button
        '''
        task = self.ids[0]
        fixed_price_stages_pool = self.env['fixed.price.stages']
        caseids = self.env['case.sheet'].search([('project_id','=',task.project_id.id)])
        if len(caseids)>0:
            case = self.env['case.sheet'].browse(caseids[0])
            for line in case.tasks_lines:
                if line.task_id.id == task.id:
                    fixed_price_stages_id = fixed_price_stages_pool.search([('name','=',line.id)])
                    for item in fixed_price_stages_id:
                        if item.invoiced:
                            raise UserWarning(_('Billed task Cannot be reactivate'))
        return super(ProjectTask, self).project_task_reevaluate()
        #Ending

    @api.multi
    def write(self, vals):
        stage = False
        if 'stage_id' in vals:
            task = self
            if task.state == 'done':
                raise UserError(_("You can't change state of already completed task"))
            stage_obj = self.env['project.task.type'].browse(vals['stage_id'])
            stage = stage_obj.name
            if stage_obj.state == 'pending':
                self.env.cr.execute('select current_date')
                current_date = self.env.cr.fetchone()[0]
                days = (datetime.strptime(current_date, '%Y-%m-%d') - datetime.strptime(task.date_deadline, '%Y-%m-%d')).days
                if days <= 0:
                    raise UserError(_("The Deadline date is not expired yet. so you can't change state to Pending"))
            elif stage_obj.state == 'draft' and task.state == 'open':
                    raise UserError(_("You can't change state to New"))


#            caseids = self.env['case.sheet'].search([('project_id','=',task.project_id.id)])
            if task.case_id:
                case = task.case_id
                # case = self.env['case.sheet'].browse(caseids[0])
                for line in case.tasks_lines:
                    if line.task_id.id == task.id:
                        #Starting // Sanal Davis // 4-6-15 //  Set warning for invoiced task if we press reevaluate button
                        fixed_price_stages_pool = self.env['fixed.price.stages']
                        fixed_price_stages_id = fixed_price_stages_pool.search([('name','=',line.id)])
                        for item in fixed_price_stages_id:
                            if item.invoiced:
                                raise UserError(_('Billed task Cannot be reactivate'))
                        # Ending
                        line.write({'state':stage})


                for line in case.associate_tasks_lines:
                    if line.task_id.id == task.id:
                        line.write([line.id], {'state':stage})
                # COMMENT THIS CODE BECAUSE DONT UPDATE STAGE ON TO DO LIST
                # for line in case.client_tasks_lines:
                #     if line.task_id.id == task.id:
                #         line.write({'state':stage})

        return super(ProjectTask, self).write(vals)

    @api.multi
    def project_task_update_deadline(self):
        task = self.ids[0]
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'wizard_update_task_deadline_id')
        except ValueError as e:
            view_id = False
        return {
            'name':_("Update Task Deadline"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'project.task.deadline',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'task_id': task.id,
                'date_deadline':task.date_deadline
            }
        }

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    task_id= fields.Many2one('case.task.line', 'Task Title')
    case_id=fields.Many2one('case.sheet', 'Case ID')

AccountAnalyticAccount()

@api.multi
def _type_get(self):
    type = [
        ('case', 'Case Sheet'),
        ('meeting', 'Meeting'),
        ('misc', 'Miscellaneous'),
        ('brow', 'Browsing/Handling Mails'),
        ('research', 'Research'),
        ('coordination', 'Coordination'),
        ]

    csm = self.env['res.users'].has_group('legal_e.group_legal_e_client_service_manager')
    if csm:
        type = [
            ('case', 'Case Sheet'),
            ('ex_meeting', 'Existing Client Meeting'),
            ('new_meeting', 'New Client Meeting'),
            ('coordination', 'Coordination'),
            ('billing', 'Billing'),
            ('bill_follow', 'Bill Follow up'),
            ('erp_update', 'ERP Update'),
            ('tele_call', 'Tele Calling'),
            ]
    lawyer = self.env['res.users'].has_group('legal_e.group_legal_e_lawyers')
    if csm and lawyer:
        type = [
            ('case', 'Case Sheet'),
            ('meeting', 'Meeting'),
            ('misc', 'Miscellaneous'),
            ('ex_meeting', 'Existing Client Meeting'),
            ('new_meeting', 'New Client Meeting'),
            ('coordination', 'Coordination'),
            ('billing', 'Billing'),
            ('bill_follow', 'Bill Follow up'),
            ('erp_update', 'ERP Update'),
            ('tele_call', 'Tele Calling'),
            ('brow', 'Browsing/Handling Mails'),
            ('research', 'Research'),
            ]
    if not csm and not lawyer:
        type = [
            ('case', 'Case Sheet'),
            ('meeting', 'Meeting'),
            ('misc', 'Miscellaneous'),
            ('ex_meeting', 'Existing Client Meeting'),
            ('new_meeting', 'New Client Meeting'),
            ('coordination', 'Coordination'),
            ('billing', 'Billing'),
            ('bill_follow', 'Bill Follow up'),
            ('erp_update', 'ERP Update'),
            ('tele_call', 'Tele Calling'),
            ('brow', 'Browsing/Handling Mails'),
            ('research', 'Research'),
            ]

    return type


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'
#
    @api.multi
    def type_get(self):
        type = [
            ('case', 'Case Sheet'),
            ('meeting', 'Meeting'),
            ('misc', 'Miscellaneous'),
            ('brow', 'Browsing/Handling Mails'),
            ('research', 'Research'),
            ('coordination', 'Coordination'),
            ]
#
        csm = self.env['res.users'].has_group('legal_e.group_legal_e_client_service_manager')
        if csm:
            type = [
                ('case', 'Case Sheet'),
                ('ex_meeting', 'Existing Client Meeting'),
                ('new_meeting', 'New Client Meeting'),
                ('coordination', 'Coordination'),
                ('billing', 'Billing'),
                ('bill_follow', 'Bill Follow up'),
                ('erp_update', 'ERP Update'),
                ('tele_call', 'Tele Calling'),
                ]
        lawyer = self.env['res.users'].has_group('legal_e.group_legal_e_lawyers')
        if csm and lawyer:
            type = [
                ('case', 'Case Sheet'),
                ('meeting', 'Meeting'),
                ('misc', 'Miscellaneous'),
                ('ex_meeting', 'Existing Client Meeting'),
                ('new_meeting', 'New Client Meeting'),
                ('coordination', 'Coordination'),
                ('billing', 'Billing'),
                ('bill_follow', 'Bill Follow up'),
                ('erp_update', 'ERP Update'),
                ('tele_call', 'Tele Calling'),
                ('brow', 'Browsing/Handling Mails'),
                ('research', 'Research'),
                ]
        if not csm and not lawyer:
            type = [
                ('case', 'Case Sheet'),
                ('meeting', 'Meeting'),
                ('misc', 'Miscellaneous'),
                ('ex_meeting', 'Existing Client Meeting'),
                ('new_meeting', 'New Client Meeting'),
                ('coordination', 'Coordination'),
                ('billing', 'Billing'),
                ('bill_follow', 'Bill Follow up'),
                ('erp_update', 'ERP Update'),
                ('tele_call', 'Tele Calling'),
                ('brow', 'Browsing/Handling Mails'),
                ('research', 'Research'),
                ]
        return type
#
    case_id= fields.Many2one('case.sheet', 'Case ID')
    court_date=fields.Date('Court Proceeding Date')
    court_proceed_id= fields.Many2one('court.proceedings', 'Proceeding')
    start_date=fields.Datetime('Start Time')
    end_date=fields.Datetime('End Time')
    type=fields.Selection(type_get, 'Related')
    employee_id=fields.Many2one('hr.employee', 'Employee')
    company_address= fields.Char('Company Address')
    contact_person=fields.Char('Contact Person')
    designation=fields.Char('Designation')
    email= fields.Char('Email')
    landline=fields.Char('Landline')
    mobile=fields.Char('Mobile')
    industry_type= fields.Char('Type of Industry')
    next_date=fields.Date('Next Followup Date')

    @api.multi
    def _check_date(self):
        for time_obj in self:
            time_sheet_ids = self.search([('start_date', '<=', time_obj.start_date), ('end_date', '>=', time_obj.end_date), ('user_id', '=', time_obj.user_id.id), ('id', '=', time_obj.id)])
            if time_sheet_ids:
                return False
        return True

    _constraints = [
        (_check_date, 'You can not have 2 timesheet that overlaps on same day!', ['start_date','end_date']),
    ]
#
    @api.model
    def create(self, vals):
        if vals.get('user_id', False):
            employee_id = self.env['hr.employee'].search([('user_id', '=', vals['user_id'])])
            if employee_id:
                vals['employee_id'] = employee_id[0]

        res = super(HrAnalyticTimesheet, self).create(vals)

        time_sheet_ids = self.search(cr, uid, [\
            ('user_id', '=', vals['user_id']),\
            ('start_date', '>=', vals['start_date'].split(' ')[0] +  ' 00:00:01'),\
            ('end_date', '<=', vals['end_date'].split(' ')[0] +  ' 11:59:58')
            ], context=context)
        unit_amount = vals['unit_amount']
        for time_obj in self.browse(cr, uid, time_sheet_ids, context=context):
            unit_amount += time_obj.unit_amount
#        if unit_amount > 15:
##            raise osv.except_osv(_('Warning!'),_('The daily maximum of timesheet duration(15 Hours) has been exceeded!'))
        return res
#
#     def write(self, cr, uid, ids, vals, context=None):
#         if vals.get('user_id', False):
#             employee_id = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', vals['user_id'])], context=context)
#             if employee_id:
#                 vals['employee_id'] = employee_id[0]
#         res = super(hr_analytic_timesheet, self).write(cr, uid, ids, vals, context=context)
#
#         if vals.get('unit_amount', False):
#             for line_obj in self.browse(cr, uid, ids, context=context):
#                 time_sheet_ids = self.search(cr, uid, [\
#                     ('user_id', '=', line_obj.user_id.id),\
#                     ('start_date', '>=', line_obj.start_date.split(' ')[0] +  ' 00:00:01'),\
#                     ('end_date', '<=', line_obj.end_date.split(' ')[0] +  ' 11:59:58')
#                     ])
#                 unit_amount = line_obj.unit_amount
#                 for time_obj in self.browse(cr, uid, time_sheet_ids, context=context):
#                     unit_amount += time_obj.unit_amount
#                 if unit_amount > 15:
#                     raise osv.except_osv(_('Warning!'),_('The daily maximum of timesheet duration(15 Hours) has been exceeded!'))
#
#         return res
#
#
#
#     def on_change_date(self, cr, uid, ids, date):
#         res = super(hr_analytic_timesheet, self).on_change_date(cr, uid, ids, date)
#         if date:
#             dt = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=14)).strftime('%Y-%m-%d')
#             current_date = time.strftime('%Y-%m-%d')
#             if dt < current_date:
#                 warning = {
#                    'title': _('Error!'),
#                    'message' : 'Your are not permitted to create timesheet for that date'
#                 }
#                 return {'value': {'date': False}, 'warning': warning}
#         return res
#
#     def onchange_start_end_date(self, cr, uid, ids, date, start_date, end_date, context=None):
#         res = {'value': {'unit_amount': 0.0}}
#         if not date or not start_date or not end_date:
#             return res
#         else:
#             start_time = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
#             end_time = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
#
#             date1 = start_time.strftime('%Y-%m-%d')
#             date2 = end_time.strftime('%Y-%m-%d')
#             warning = {
#                    'title': _('Error!'),
#                    'message' : 'Start time and end time must be in the same date as the record date'
#                 }
#             if date != date1:
#                 return {'value': {'start_date': False}, 'warning': warning}
#             if date != date2:
#                 return {'value': {'end_date': False}, 'warning': warning}
#             time_difference = end_time - start_time
#             hour = time_difference.total_seconds() / 60 / 60
#             res['value']['unit_amount'] = hour
#         return res
#
#     def onchange_case_id(self, cr, uid, ids, case_id, court_proceed_id, context=None):
#         res = {'value': {'account_id': False}}
#         if not case_id:
#             res['value']['account_id'] = self._get_default_timesheet_analytic_account(cr, SUPERUSER_ID, context=context)
#             return res
#         else:
#             case_obj = self.pool.get('case.sheet').browse(cr, SUPERUSER_ID, case_id, context=context)
#             res['value']['type'] = 'case'
#             if court_proceed_id:
#              court_obj = self.pool.get('court.proceedings').browse(cr, SUPERUSER_ID, court_proceed_id, context=context)
#              if court_obj.case_id.id != case_id:
#                 res['value']['case_id'] = court_obj.case_id.id
#                 res['value']['account_id'] = court_obj.case_id.project_id.analytic_account_id.id
#                 return res
#             if case_obj.project_id and case_obj.project_id.analytic_account_id:
#                 res['value']['account_id'] = case_obj.project_id.analytic_account_id.id
#         return res
#
#     def onchange_type(self, cr, uid, ids, type, case_id,context=None):
#         res = {'value': {'case_id': False}}
#         if not type:
#             return res
#         else:
#             res['value']['case_id'] = case_id
#             if type == 'misc':
#                 res['value']['case_id'] = False
#                 res['value']['account_id'] = self._get_default_timesheet_analytic_account(cr, uid, context=context)
#         return res
#
#     def onchange_court_proceed_id(self, cr, uid, ids, court_proceed_id, context=None):
#         res = {'value': {'case_id': False}}
#         if not court_proceed_id:
#             return res
#         else:
#             court_obj = self.pool.get('court.proceedings').browse(cr, uid, court_proceed_id, context=context)
#             if court_obj.case_id:
#                 res['value']['case_id'] = court_obj.case_id.id
#         return res
#
# hr_analytic_timesheet()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def update_dept(self):
        try:
            dummy, view_id = self.env['ir.model.data'].get_object_reference('legal_e', 'wizard_update_emp_dept_id')
        except ValueError as e:
            view_id = False
        return {
            'name':_("Update Employee Department"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hr.employee.update.dept',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'emp_ids': self.ids
            }
        }
HrEmployee()


class OtherExpenses(models.Model):
    _name = 'other.expenses'
    _description = 'Other Expenses'

    case_id = fields.Many2one('case.sheet','File Number')
    name=fields.Char('Description',size=200)
    date=fields.Date('Requested Date')
    req_amount=fields.Float('Requested Amount')
    paid_amount = fields.Float('Amount Paid')
    billable=fields.Selection([('bill','Billable'),('nobill','Not Billable')],'Billable')
    expense_type = fields.Selection([('other_cash','Additional Miscellaneous Expense'),('adv_billing', 'Advance Billing'),
                                     ('associate_pay','Associate Payment'),('petty_cash', 'Branch Petty Cash Expense'),
                                     ('third_pp','Third Party Payout')], 'Expense Type')
    amount=fields.Float('Amount')
    billed_amount=fields.Float('Amount Billed')
    invoiced=fields.Boolean('Invoiced ?')
    invoice_id = fields.Many2one('account.invoice', string='Bill No.')
    invoice_status = fields.Selection(related='invoice_id.state', store=True, readonly=True, string='Bill Status')
    old_id=fields.Many2one('other.expenses','Old ID')
    expense_id=fields.Many2one('hr.expense', 'Expense')

    @api.multi
    def copy_data(self, default=None):
        default = default or {}
        default.update({
            'invoiced':False
        })
        return super(OtherExpenses, self).copy_data(default)

#    @api.multi
#    def unlink(self):
#        for obj in self:
#            if obj.expense_line_id:
#                raise UserError(_('Error!'),_('You cannot delete an Expense Line.This record is associated with HR expense.'))
#
#        return super(OtherExpenses, self).unlink()


class HrExpense(models.Model):
    _inherit = 'hr.expense'
    _description = 'HR Expense with case sheet'

    case_id = fields.Many2one('case.sheet', 'Case Sheet')
    req_amount = fields.Float('Requested Amount')
    paid_amount = fields.Float('Amount to be Paid')
    billable = fields.Selection([('bill', 'Billable'), ('nobill', 'Not Billable')], 'Billable')
    expense_type = fields.Selection([('other_cash','Additional Miscellaneous Expense'),('adv_billing', 'Advance Billing'),
                                     ('associate_pay','Associate Payment'),('petty_cash', 'Branch Petty Cash Expense'),
                                     ('third_pp','Third Party Payout')], 'Expense Type')
    product_id = fields.Many2one('product.product', string='Product', readonly=True,
                                 states={'draft': [('readonly', False)], 'refused': [('readonly', False)]},
                                 domain=[('can_be_expensed', '=', True)])
    office_id = fields.Many2one('ho.branch', 'Office')
    partner_id = fields.Many2one('res.partner', 'Associate/Vendor')

    @api.model
    def create(self, values):
        other_exp_id = self.env['other.expenses'].search([('case_id', '=', values.get('case_id', False)), ('name', '=', values.get('name', False))])
        if other_exp_id:
            raise UserError(_("Expense name is already exist!"))
        res = super(HrExpense, self).create(values)
        if res and res.case_id:
            self.env['other.expenses'].create({
                'case_id': res.case_id.id,
                'name': res.name,
                'date': res.date,
                'req_amount': res.unit_amount,
                'paid_amount': res.paid_amount,
                'billable': res.billable,
                'expense_type': res.expense_type,
                'expense_id': res.id
            })
        return res

    @api.multi
    def write(self, vals):
        res = super(HrExpense, self).write(vals)
        if 'expense_type' in vals:
            other_exp_id = self.env['other.expenses'].search([('case_id', '=', self.case_id.id), ('expense_id', '=', self.id)])
            if other_exp_id:
                other_exp_id.expense_type = vals['expense_type']
        return res

    @api.multi
    def submit_expenses(self):
        other_exp_id = self.env['other.expenses'].search([('case_id', '=', self.case_id.id), ('expense_id', '=', self.id)])
        if not other_exp_id:
            self.env['other.expenses'].create({
                'case_id': self.case_id.id,
                'name': self.name,
                'date': self.date,
                'req_amount': self.unit_amount,
                'paid_amount': self.paid_amount,
                'billable': self.billable,
                'expense_type': self.expense_type,
                'expense_id': self.id,
            })
        if any(expense.state != 'draft' for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report!"))
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'context': {
                'default_expense_line_ids': [line.id for line in self],
                'default_employee_id': self[0].employee_id.id,
                'default_name': self[0].name if len(self.ids) == 1 else ''
            }
        }

    @api.multi
    def unlink(self):
        other_exp_id = self.env['other.expenses'].search([('case_id', '=', self.case_id.id), ('expense_id', '=', self.id)])
        if other_exp_id:
            other_exp_id.unlink()
        return super(HrExpense, self).unlink()


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    _description = "Expense Report"
    
    def _get_assignee(self):
        for exp_sheet_obj in self:
            expense_id = self.env['hr.expense'].search([('sheet_id','=',exp_sheet_obj.id)])
            if expense_id and expense_id[0].case_id:
                exp_sheet_obj.assignee_id=expense_id[0].case_id.assignee_id.id

    state = fields.Selection([('submit', 'Submitted'),
                              ('approve', 'Approved'),
                              ('waiting_special', 'Waiting for Special Approval'),
                              ('special_approve', 'Special Approved'),
                              ('post', 'Posted'),
                              ('done', 'Paid'),
                              ('cancel', 'Refused')
                              ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False,
                             default='submit', required=True,
                             help='Expense Report State')
    assignee_id = fields.Many2one('hr.employee',compute='_get_assignee', string='Assignee',store=True)


    @api.multi
    def approve_expense_sheets(self):
        for expense_line in self.expense_line_ids:
            if expense_line.paid_amount <= 0.00:
                raise UserError(_("Please update Amount Paid value!"))
#        if not self.user_has_groups('hr_expense.group_hr_expense_user'):
#            raise UserError(_("Only HR Officers can approve expenses"))
        self.write({'state': 'approve', 'responsible_id': self.env.user.id})
        # if self.state == 'approve':
        #     for expense_line in self.expense_line_ids:
        #         self.env['other.expenses'].create({
        #             'case_id': expense_line.case_id.id,
        #             'name': expense_line.name,
        #             'date': expense_line.date,
        #             'req_amount': expense_line.unit_amount,
        #             'paid_amount': expense_line.paid_amount,
        #             'billable': expense_line.billable,
        #             'expense_type': expense_line.expense_type,
        #         })

    # send for special approval
    @api.multi
    def action_send_for_special_approval(self):
        group = self.env['res.groups'].search([('name', '=', 'Special Approve Expense')])
        if group:
            user_ids = self.env['res.users'].sudo().search([('groups_id', 'in', [group.id])])
            email_to = ''.join([user.partner_id.email + ',' for user in user_ids])
            email_to = email_to[:-1]
        else:
            email_to = self.user_id.partner_id.email
        ctx = dict(self.env.context or {})
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        fragment = {
            'model': 'hr.expense.sheet',
            'view_type': 'form',
            'id': self.id,
        }
        url = urllib.parse.urljoin(base_url,
                                   "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_send_for_special_approval', raise_if_not_found=False)
        ctx.update({
            'expense_id': self.name,
            'url_link': url,
            'email_to': email_to,
        })
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
        return self.write({'state': 'waiting_special'})

    @api.multi
    def special_approve_expense_sheets(self):
        self.write({'state': 'special_approve', 'responsible_id': self.env.user.id})

    @api.multi
    def action_sheet_move_create_journal(self):
        # self.write({'state': 'post'})
        # if self.payment_mode == 'own_account':
        #     self.write({'state': 'post'})
        view_id = self.env.ref('account.view_move_form').id
        return {
            'name': 'Journal Entries',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'account.move',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_expense_id': self.expense_line_ids[0].id,
                        'default_ref': self.name,
                        'default_exp_paid_amount': self.expense_line_ids[0].paid_amount,
                        'company_id': self.env.user.company_id.id,
                        'default_is_expense': True},
        }

    @api.multi
    def reset_expense_sheets(self):
        self.mapped('expense_line_ids').write({'is_refused': False})
        for expense in self.expense_line_ids:
            self.env['other.expenses'].create({
                'case_id': expense.case_id.id,
                'name': expense.name,
                'date': expense.date,
                'req_amount': expense.unit_amount,
                'paid_amount': expense.paid_amount,
                'billable': expense.billable,
                'expense_type': expense.expense_type,
                'expense_id': expense.id,
            })
        return self.write({'state': 'submit'})

    @api.multi
    def unlink(self):
        for expense in self.expense_line_ids:
            other_exp_id = self.env['other.expenses'].search([('case_id', '=', expense.case_id.id), ('expense_id', '=', expense.id)])
            if other_exp_id:
                other_exp_id.unlink()
        return super(HrExpenseSheet, self).unlink()


class AccountMove(models.Model):
    _inherit = 'account.move'

    expense_id = fields.Many2one('hr.expense', string='Expense Id', store=True, readonly=True)
    is_expense = fields.Boolean('Is Expense', default=False)
    exp_paid_amount = fields.Float('Amount to be Paid', store=True, readonly=True)

    @api.multi
    def post(self):
        result = super(AccountMove, self).post()
        if self.expense_id:
            self.expense_id.sheet_id.write({'account_move_id': self.id, 'state': 'post'})
            other_expense_id = self.env['other.expenses'].search([('expense_id', '=', self.expense_id.id),
                                                          ('case_id', '=', self.expense_id.case_id.id)])
            if other_expense_id:
                other_expense_id.write({'paid_amount': self.exp_paid_amount})
        return result

# class HrExpense(models.Model):
#     _inherit = 'hr.expense'
#     _description = 'HR Expense with case sheet'
#
#     def default_get(self, cr, uid, fields_list, context=None):
#         if not context:
#             context = {}
#         res = super(hr_expense_expense, self).default_get(cr, uid, fields_list, context=context)
#         if context.has_key('case_id'):
#             res.update({'case_id':context.get('case_id', False)})
#         return res
#
#     def expense_accept(self, cr, uid, ids, context=None):
#         res = super(hr_expense_expense, self).expense_accept(cr, uid, ids, context=context)
#         for expense_obj in self.browse(cr, uid, ids, context=context):
#             if expense_obj.case_id:
#                 for line_obj in expense_obj.line_ids:
#                     vals = {
#                         'case_id': expense_obj.case_id.id,
#                         'name': line_obj.name,
#                         'date': line_obj.date_value,
#                         'amount': line_obj.total_amount,
#                         'billable': line_obj.is_billable and 'bill' or 'nobill',
#                         'to_whom': expense_obj.employee_id.name,
#                         'expense_line_id': line_obj.id
#                         }
#                     self.pool.get('other.expenses').create(cr, uid, vals, context=context)
#         return res
#
#
#     def action_receipt_create(self, cr, uid, ids, context=None):
#         for exp_obj in self.browse(cr, uid, ids, context=context):
#             for line_obj in exp_obj.line_ids:
#                 if not line_obj.account_id:
#                     raise osv.except_osv(_('Error!'),_('Please fill accounts in Expense Lines.'))
#
#
#         res = super(hr_expense_expense, self).action_receipt_create(cr, uid, ids, context=context)
#         for exp_obj in self.browse(cr, uid, ids, context=context):
#             if exp_obj.account_move_id:
#                 self.pool.get('account.move').button_validate(cr, uid, [exp_obj.account_move_id.id], context=context)
#         return res
#
#
#     def move_line_get_item(self, cr, uid, line, context=None):
#         res = {
#             'type':'src',
#             'name': line.name.split('\n')[0][:64],
#             'price_unit':line.unit_amount,
#             'quantity':line.unit_quantity,
#             'price':line.total_amount,
#             'account_id':line.account_id.id,
#             'product_id':line.product_id.id,
#             'uos_id':line.uom_id.id,
#             'account_analytic_id':line.analytic_account.id,
#             'case_id': line.expense_id.case_id and line.expense_id.case_id.id or False,
#             'office_id': line.expense_id.case_id and line.expense_id.case_id.ho_branch_id.id or False,
#             }
#         return res
#
#
#     def line_get_convert(self, cr, uid, x, part, date, context=None):
#         res = super(hr_expense_expense, self).line_get_convert(cr, uid, x, part, date, context=context)
#         res.update({
#             'case_id': x.get('case_id', False),
#             'office_id': x.get('office_id', False),
#             })
#         return res

#     def invoice_pay_employee(self, cr, uid, ids, context=None):
#         if not ids: return []
#         dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')
#         exp_obj = self.browse(cr, uid, ids[0], context=context)
#         return {
#             'name':_("Pay Expense"),
#             'view_mode': 'form',
#             'view_id': view_id,
#             'view_type': 'form',
#             'res_model': 'account.voucher',
#             'type': 'ir.actions.act_window',
#             'nodestroy': True,
#             'target': 'new',
#             'domain': '[]',
#             'context': {
#                 'payment_expected_currency': exp_obj.company_id.currency_id.id,
#                 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(exp_obj.employee_id.user_id.partner_id).id,
#                 'default_amount': exp_obj.amount,
#                 'default_reference': exp_obj.name,
#                 'close_after_process': True,
#                 'invoice_type': 'in_invoice',
#                 'default_type': 'payment',
#                 'type': 'payment'
#             }
#         }

# hr_expense_expense()


# class hr_expense_line(osv.osv):
#     _inherit = 'hr.expense.line'
#     _columns = {
#         'is_billable': fields.boolean('Billable'),
#         'account_id': fields.Many2one('account.account', 'Account'),
#         }
#
#     def write(self, cr, uid, ids, vals, context=None):
#         if vals:
#             for line_obj in self.browse(cr, uid, ids, context=context):
#                 if line_obj.expense_id.state != 'draft':
#
#                     if line_obj.expense_id.state == 'accepted' and self.pool.get('res.users').has_group(cr, uid, 'account.group_account_manager') \
#                          and not vals.get('is_billable', False) and not vals.get('unit_amount', False) and not vals.get('unit_quantity', False):
#                         pass
#                     else:
#                         raise osv.except_osv(_('Warning!'), _('You are not permitted to edit this record.'))
#
#         return super(hr_expense_line, self).write(cr, uid, ids, vals, context=context)
#
# hr_expense_line()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'office in Account move line'

    office_id=fields.Many2one('ho.branch','Office') #Add offfice in Account move line
    case_id=fields.Many2one('case.sheet','Case Sheet') #Add case sheet in Account Move Line
    department_id=fields.Many2one('hr.department', 'Department')
    cost_id=fields.Many2one('legal.cost.center',related='department_id.cost_id',string="Cost Center", store=True)

    # override reconcile method and add account_move_ids logic
    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        res = super(AccountMoveLine, self).reconcile(writeoff_acc_id=writeoff_acc_id,
                                                     writeoff_journal_id=writeoff_journal_id)
        # for record in self:
        #     account_move_ids = [l.move_id.id for l in record.expense_id.sheet_id.account_move_id.line_ids]
        #     if account_move_ids:
        #         expense_sheets = self.env['hr.expense.sheet'].search([
        #             ('account_move_id', 'in', account_move_ids), ('state', '!=', 'done')
        #         ])
        #         expense_sheets.set_to_paid()
        for record in self:
            if record.move_id and record.move_id.state == 'posted':
                record.expense_id.sheet_id.set_to_paid()
        return res


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    # _name = "hr.expense.sheet.register.payment.wizard"
    _inherit = "hr.expense.sheet.register.payment.wizard"
    _description = "Expense Report Register Payment wizard"

    # override expense_post_payment method and add expense_id logic
    @api.multi
    def expense_post_payment(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)

        # Create payment and post it
        payment = self.env['account.payment'].create(self._get_payment_vals())
        payment.post()

        # Log the payment in the chatter
        body = (_(
            "A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") % (
                payment.amount, payment.currency_id.symbol,
                url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, expense_sheet.name))
        expense_sheet.message_post(body=body)

        # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in payment.move_line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable':
                account_move_lines_to_reconcile |= line
        expense_id = self.env['hr.expense'].search([('sheet_id', '=', expense_sheet.id)])
        account_move_lines_to_reconcile.write({'expense_id': expense_id.id})
        account_move_lines_to_reconcile.reconcile()

        return {'type': 'ir.actions.act_window_close'}


class HrExpenseRefuseWizard(models.TransientModel):
    _inherit = "hr.expense.refuse.wizard"
    _description = "Expense refuse Reason wizard"

    @api.multi
    def expense_refuse_reason(self):
        self.ensure_one()
        if self.hr_expense_ids:
            self.hr_expense_ids.refuse_expense(self.reason)
            for each_exp in self.hr_expense_ids:
                other_exp_id = self.env['other.expenses'].search([('case_id', '=', each_exp.case_id.id), ('expense_id', '=', each_exp.id)])
                if other_exp_id:
                    other_exp_id.unlink()
        if self.hr_expense_sheet_id:
            self.hr_expense_sheet_id.refuse_sheet(self.reason)
            for expense in self.hr_expense_sheet_id.expense_line_ids:
                other_exp_id = self.env['other.expenses'].search([('case_id', '=', expense.case_id.id), ('expense_id', '=', expense.id)])
                if other_exp_id:
                    other_exp_id.unlink()
        return {'type': 'ir.actions.act_window_close'}
