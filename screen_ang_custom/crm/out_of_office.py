# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models,fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class OutOfOffice(models.Model):
    _name = 'out.of.office'    
        
    def _get_count(self):
        res = {}
        for line in self:
            start_dt = datetime.strptime(line.start_date, '%Y-%m-%d')        
            end_dt = datetime.strptime(line.end_date, '%Y-%m-%d')
            duration = ((end_dt - start_dt).days + 1)
            res[line.id] = duration
        return res

    name=fields.Char('Subject')
    user_id=fields.Many2one('res.users','Person', default=lambda self:self.env.user.id)
    reason=fields.Text('Reason')
    type=fields.Selection([('days','Days'),('hours','Hours')],'Out for')
    event_type=fields.Selection([('birthdays','Birthdays'),('outofoffice','Out of Office')],'Event Type', default='outofoffice')
    start_date=fields.Date('From Date')
    end_date=fields.Date('To Date')
    start_time=fields.Float('From Time')
    end_time=fields.Float('To Time')
    count=fields.Float(compute='_get_count', string='Total Number')

    # _defaults = {
    #     'user_id': lambda self, cr, uid, context=None: uid,
    #     'event_type': lambda *a : 'outofoffice',
    # }

    @api.model
    def create(self, vals):
        retvals = super(OutOfOffice, self).create(vals)
        
        if retvals:
            line = retvals
            # line = self.browse(retvals)
            line.validate_dates(line.start_date, line.end_date, line.event_type, line.type)
            line.validate_times(line.start_time, line.end_time, line.event_type, line.type)
            # self.validate_dates([line.id], line.start_date, line.end_date, line.event_type, line.type)
            # self.validate_times([line.id], line.start_time, line.end_time, line.event_type, line.type)
        
        return retvals

    @api.multi
    def write(self, vals):
        retvals = super(OutOfOffice, self).write(vals)
        for line in self:
            self.validate_dates([line.id], line.start_date, line.end_date, line.event_type, line.type)
            self.validate_times([line.id], line.start_time, line.end_time, line.event_type, line.type)
        return retvals    

    # @api.onchange('start_date','end_date','event_type','type')
    @api.multi
    def validate_dates(self,start_date,end_date,event_type,type):
        if event_type != 'outofoffice' or type != 'days':
            return {'value':{}}
        from_date = False
        to_date = False
        if start_date:
            from_date = datetime.strptime(start_date.split(' ')[0], '%Y-%m-%d')
        if end_date:
            to_date = datetime.strptime(end_date.split(' ')[0], '%Y-%m-%d')
            
        if from_date:
            if to_date and (to_date - from_date).days < 0:
                raise UserError(_('Warning'),_('From Date Should be Less than/ Equal to To Date'))
                return {'value': {'start_date':False}}
        if to_date:
            if from_date and (to_date - from_date).days < 0:
                raise UserError(_('Warning'),_('To Date Should be Greater than/ Equal to From Date'))
                return {'value': {'end_date':False}}
        return {'value': {}}

    # @api.onchange('start_date', 'end_date', 'event_type', 'type')
    @api.multi
    def validate_times(self,start_time,end_time,event_type,type):
        if event_type != 'outofoffice' or type != 'hours':
            return {'value':{}}
        if start_time and end_time:
            if (end_time - start_time) < 0:
                raise UserError(_('Warning'),_('From Time Should be Less than/ Equal to To Time'))
                return {'value': {'start_date':False}}
        
        return {'value': {}}
        

OutOfOffice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: