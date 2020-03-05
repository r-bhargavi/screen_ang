# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api
import urllib.parse


class CaseClose(models.TransientModel):
    _name = "case.close"
    _description = "To Close the Case Sheet"

    name = fields.Text('Remarks')
    close_date = fields.Date('Close Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    closure_type = fields.Selection([('return', 'Return'), ('retain', 'Retain'), ('destroy', 'Destroy')],
                                    'Closure Type', required=True)
    time_duration = fields.Selection([('1month', '1 Month'), ('3month', '3 Months'), ('6month', '6 Months'),
                             ('12month', '12 Months')], 'Time Duration', required=True)

    @api.multi
    def case_sheet_closure_request(self):
        ctx = dict(self.env.context or {})
        case_id = self.env['case.sheet'].browse(self._context.get('active_id', False))
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        query = {'db': self._cr.dbname}
        fragment = {
            'model': 'case.sheet',
            'view_type': 'form',
            'id': case_id.id,
        }
        url = urllib.parse.urljoin(base_url, "/web?%s#%s" % (urllib.parse.urlencode(query), urllib.parse.urlencode(fragment)))
        template_id = self.env.ref('legal_e.email_template_for_case_closure_request', raise_if_not_found=False)
        ctx.update({
            'case_id': case_id.name,
            'url_link': url,
            'assignee_id': case_id.assignee_id.work_email,
        })
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
        case_id.write({
            'close_comments': self.name,
            'close_date': self.close_date,
            'closure_type': self.closure_type,
            'time_duration': self.time_duration,
            'case_close': True,
            'state': 'waiting_assignee'
        })
