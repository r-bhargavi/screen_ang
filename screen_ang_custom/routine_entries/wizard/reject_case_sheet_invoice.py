# -*- coding: utf-8 -*-
from odoo import fields, models, api
import urllib.parse


class RejectCaseSheetInvoice(models.TransientModel):
    _name = "reject.case.sheet.invoice"
    _description = "Reject Case Sheet Invoice"

    name = fields.Text('Remarks')

    @api.multi
    def reject_case_sheet_invoice(self):
        casesheet_id = self.env['case.sheet.invoice'].browse(self._context.get('active_id', False))
        if casesheet_id.case_id.client_service_executive_id.work_email:
            email_to = casesheet_id.case_id.client_service_executive_id.work_email
        else:
            email_to = self.user_id.partner_id.email
        ctx = dict(self.env.context or {})
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        fragment = {
            'model': 'case.sheet.invoice',
            'view_type': 'form',
            'id': casesheet_id.id,
        }
        url = urllib.parse.urljoin(base_url,
                                   "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_for_case_entry_reject_request', raise_if_not_found=False)
        ctx.update({
            'casesheet_id': casesheet_id.name,
            'reason': self.name,
            'url_link': url,
            'email_to': email_to,
        })
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
        casesheet_id.write({'reject_comment': self.name, 'state': 'rejected'})
