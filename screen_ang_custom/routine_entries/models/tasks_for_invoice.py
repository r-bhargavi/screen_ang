# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class TasksForInvocie(models.Model):
    _name = 'tasks.for.invoice'    

    @api.multi
    def _get_invoiced_total(self, field_name):
        res = {}        
        for line in self:
            total = 0.0
            if line.invoice_id:
                inv = self.env['account.invoice'].browse(line.invoice_id.id)
                total = inv.amount_total
            res[line.id] = total    
        return res

    @api.multi
    def _get_invoiced_balance(self, field_name):
        res = {}          
        for line in self:
            residual = 0.0
            if line.invoice_id:
                inv = self.env['account.invoice'].browse(line.invoice_id.id)
                residual = inv.residual 
            res[line.id] = residual
        return res

    @api.multi
    def _get_invoiced_state(self, field_name):
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

    # case_id= fields.Many2one('case.sheet', 'Case Sheet No.', readonly=True)
    # name=fields.Many2one('case.tasks.line','Task Related', required=True, readonly=True)
    assignee_id= fields.Many2one('hr.employee', 'Assignee', readonly=True)
    amount= fields.Float('Amount', readonly=True)
    state=fields.Selection([('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Completed','Completed'),('Invoiced','Invoiced')],'Status', readonly=True, default='New')
    invoiced=fields.Boolean('Invoiced')
    invoice_id=fields.Many2one('account.invoice','Invoice ID')
    fixed_price_task_id=fields.Many2one('fixed.price.stages', 'Fixed Price Task ID')
    tm_task_id=fields.Many2one('tm.line', 'T & M Task ID')
    inv_state= fields.Char(compute='_get_invoiced_state',string='INV Status', readonly=True)
    inv_total_amt=fields.Float(compute='_get_invoiced_total',string='Total INV Amt',readonly=True)
    inv_balance_amt=fields.Float(compute='_get_invoiced_balance',string='Balance INV Amt',readonly=True)

    # _defaults = {
    # 	'state':'New',
    # }

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
            product_id=False
            name=line.name.name
            if line.name.name.product_id:
                product_id = line.name.name.product_id.id
                name= line.name.name.name
            inv_id = self.env['account.invoice'].create({'partner_id':partner_id,'account_id':acc_id,'invoice_line':[(0, 0, {'product_id':product_id,'name':name, 'quantity':1.0,'price_unit':line.amount,'type':'out_invoice'})]},context)
            # self.write(cr, uid, [line.id], {'invoiced':True,'invoice_id':inv_id})
            line.write({'invoiced':True,'invoice_id':inv_id})
            if line.fixed_price_task_id:
                # self.pool.get('fixed.price.stages').write(cr, uid, [line.fixed_price_task_id.id], {'invoiced':True,'invoice_id':inv_id})
                line.fixed_price_task_id.write({'invoiced':True,'invoice_id':inv_id})
            if line.tm_task_id:
                # self.pool.get('tm.line').write(cr, uid, [line.tm_task_id.id], {'invoiced':True,'invoice_id':inv_id})
                line.tm_task_id.write({'invoiced':True,'invoice_id':inv_id})
        return True

    @api.onchange('percent','fixed_price')
    def onchange_percent(self):
        
        if self.fixed_price:
            amount = (self.fixed_price*self.percent)/100
            return {'value':{'amount':amount}}
        else:
            raise UserError(_('Error!'),_('Enter the Fixed Price Amount First!'))
        return {'value':{'amount':0,'percent_amount':0}}

    @api.onchange('amount','fixed_price')
    def onchange_amount(self):
        if self.fixed_price:
            percent_amount = (100*self.amount)/self.fixed_price
            return {'value':{'percent_amount':percent_amount}}
        else:
            raise UserError(_('Error!'),_('Enter the Fixed Price Amount First!'))
        return {'value':{'percent_amount':0,'amount':0}}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: