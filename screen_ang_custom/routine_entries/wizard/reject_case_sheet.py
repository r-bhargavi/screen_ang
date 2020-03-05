# -*- coding: utf-8 -*-
from odoo import fields, models, api
import urllib.parse


class RejectCaseSheet(models.TransientModel):
    _name = "reject.case.sheet"
    _description = "Reject Case Sheet"

    name = fields.Text('Remarks')

    @api.multi
    def reject_case_sheet(self):
        casesheet_id = self.env['case.sheet'].browse(self._context.get('active_id', False))
        group = self.env['res.groups'].search([('name', '=', 'Case Entry Request Group')])
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
            'id': casesheet_id.id,
        }
        url = urllib.parse.urljoin(base_url,
                                   "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_for_case_sheet_reject_request', raise_if_not_found=False)
        ctx.update({
            'casesheet_id': casesheet_id.name,
            'client_id': casesheet_id.client_id.name,
            'ho_branch_id': casesheet_id.ho_branch_id.name,
            'client_service_executive_id': casesheet_id.client_service_executive_id.name,
            'client_service_manager_id': casesheet_id.client_service_manager_id.name,
            'casetype_id': casesheet_id.casetype_id.name,
            'reason': self.name,
            'url_link': url,
            'email_to': email_to,
        })
        template_id.with_context(ctx).send_mail(casesheet_id.id, force_send=True)
        casesheet_id.write({'reject_comment': self.name, 'state': 'sheet_rejected'})
