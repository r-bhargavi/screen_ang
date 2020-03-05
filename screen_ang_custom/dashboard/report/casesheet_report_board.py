# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo import tools


class CasesheetReportBoard(models.Model):
    _name = "casesheet.report.board"
    _table = 'casesheet_report_board'
    _description = "Open and Completed Case Sheets by Type of work"
    _auto = False
    _order="year,month"

    name=fields.Char('File Number', size=128, readonly=True)
    date=fields.Date('Date', readonly=True)
    nbr= fields.Integer('# of Case Sheets', readonly=True)
    state= fields.Selection([
        ('new', 'New'),
        ('inprogress', 'In Progress'),
        ('cancel', 'Cancelled'),
        ('transfer','Transferred'),
        ('won', 'Won'),
        ('arbitrated', 'Arbitrated'),
        ('withdrawn', 'With Drawn'),
        ('lost', 'Lost'),
        ('inactive', 'Inactive'),
        ('done', 'Closed'),
            ], 'Status', readonly=True)
    month=fields.Integer('Month')
    year=fields.Integer('Year')
    year_month=fields.Integer('Year Month')
    work_type=fields.Selection([
        ('civillitigation', 'Civil Litigation'),
        ('criminallitigation', 'Criminal Litigation'),
        ('non_litigation', 'Non Litigation'),
        ('arbitration', 'Arbitration'),
        ('execution', 'Execution'),
        ('mediation', 'Mediation')], 'Type of Work',readonly=True)

    # def init(self):
    #     # tools.drop_view_if_exists('casesheet_report_board')
    #     self.env.cr.execute("""
    #         create view casesheet_report_board as (
    #             select
    #                 c.date::varchar||'-'||c.id::varchar AS id,
    #                 c.date as date,
    #                 1 as nbr,
    #                 c.name as name,
    #                 c.state as state,
    #                 to_char(c.date, 'YYYY')::integer as year,
    #                 to_char(c.date, 'MM')::integer as month,
    #                 to_char(c.date, 'YYYY-MM-DD') as day,
    #                 c.work_type as work_type,
    #                  (to_char(c.date, 'YYYY')||to_char(c.date, 'MM'))::integer AS year_month
    #
    #             from case_sheet c
    #              order by year,month
    #         )
    #         """)
    
CasesheetReportBoard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: