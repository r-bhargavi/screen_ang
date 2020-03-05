# -*- coding: utf-8 -*-
from odoo import fields, models, api
import urllib.parse


class RejectCaseClosureAssignee(models.TransientModel):
    _name = "reject.case.closure.assignee"
    _description = "Reject Case Closure Assignee"

    name = fields.Text('Remarks')

    @api.multi
    def reject_case_closure_assignee(self):
        casesheet_id = self.env['case.sheet'].browse(self._context.get('active_id', False))
        ctx = dict(self.env.context or {})
        case_id = self.env['case.sheet'].browse(self._context.get('active_id', False))
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        fragment = {
            'model': 'case.sheet',
            'view_type': 'form',
            'id': case_id.id,
        }
        url = urllib.parse.urljoin(base_url,
                                   "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_for_case_closure_reject_assignee', raise_if_not_found=False)
        ctx.update({
            'case_id': case_id.name,
            'url_link': url,
            'client_service_executive_id': case_id.client_service_executive_id.work_email,
        })
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
        casesheet_id.write({'assignee_case_closure_reject': self.name, 'state': 'inprogress'})
