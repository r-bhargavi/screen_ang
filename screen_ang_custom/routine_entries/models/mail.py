#!/usr/bin/env python2
#encoding: UTF-8

from odoo import fields, models, api


class CustomSendMail(models.Model):
    _name = 'custom.send.mail'
    
    partner_ids=fields.Many2many('res.partner', 'res_partner_custom_send_mail_relation','custom_send_mail_id','partner_id' ,string='Recipients', track_visibility='onchange', ondelete="restrict", required=True)
    subject=fields.Char('Subject',required='1')
    template_id=fields.Many2one('mail.template', string='Mail Template', ondelete="restrict", required=True)
    group=fields.Many2one('res.group', string='Group')
    
    @api.multi
    def send_mail(self,recipients,template,context):
        if template and context.get('browse_object') and context.get('record'):
            if context.get('res_user')=='res_user':
                for group_id in recipients:
                    email_to= [(4, pid) for pid in group_id.user]
                    template.send_mail(record_id, force_send=True,
                               email_values={'email_to': email_to,
                                             'model': model})
            elif context.get('res_partner')=='res_partner':
                email_to= [(4, pid) for pid in recipients]
                model=context.get('browse_object')
                record_id=context.get('record')
                mail_id=template.send_mail(record_id, force_send=True,
                                   email_values={'email_to': email_to,
                                                 'model': model})
        
    @api.multi
    def action_send_mail(self):
        context={'res_partner':'res_partner','browse_object':'sale.order'}
        self.send_mail(self.partner_ids,self.template_id,context)