# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_pan_no=fields.Char('PAN Number', size=40)
    expense_account_ids= fields.Many2many('account.account', 'company_accounts', 'company_id', 'account_id','Expense Accounts')
    proceed_stage_id= fields.Many2one('court.proceedings.stage', 'Closing Stage')
    we_thank_you = fields.Text(string='Initial Lines in SOW')
    scope_of_work = fields.Text(string='Scope of Work')
    annexure_one = fields.Text(string='Annexure 1')
    annexure_three = fields.Text(string='Annexure 3')
    nl_we_thank_you = fields.Text(string='Initial Lines in SOW')
    nl_scope_of_work = fields.Text(string='Scope of Work')
    nl_annexure_one = fields.Text(string='Annexure 1')
    nl_annexure_three = fields.Text(string='Annexure 3')
