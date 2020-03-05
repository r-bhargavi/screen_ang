# -*- coding: utf-8 -*-
import base64
import logging
from urllib import urlencode, quote as quote
from odoo import netsvc
from odoo import models, fields, api,_
from odoo import tools


_logger = logging.getLogger(__name__)

try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': quote,
        'urlencode': urlencode,
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")

class MailTemplate(models.Model):
    "Templates for sending email"
    _inherit = "mail.template"
    _description = 'Email Templates'
    _order = 'name'

    @api.multi
    def generate_email(self, res_id, context=None):
        """Generates an email from the template for given (model, res_id) pair.

           :param template_id: id of the template to render.
           :param res_id: id of the record to use for rendering the template (model
                          is taken from template definition)
           :returns: a dict containing all relevant fields for creating a new
                     mail.mail entry, with one extra key ``attachments``, in the
                     format expected by :py:meth:`mail_thread.message_post`.
        """
        # if context is None:
        #     context = {}
        report_xml_pool = self.env['ir.actions.report.xml']
        template = self.get_email_template(res_id)
        values = {}
        for field in ['subject', 'body_html', 'email_from',
                      'email_to', 'email_recipients', 'email_cc', 'reply_to']:
            if field in context:
                values[field] = context[field]    
            else:    
                values[field] = self.render_template(getattr(template, field),
                                                 template.model, res_id) \
                                                 or False
        if template.user_signature:
            signature = self.env['res.users'].browse(self.env.user.id, context).signature
            values['body_html'] = tools.append_content_to_html(values['body_html'], signature)

        if values['body_html']:
            values['body'] = tools.html_sanitize(values['body_html'])

        values.update(mail_server_id=template.mail_server_id.id or False,
                      auto_delete=template.auto_delete,
                      model=template.model,
                      res_id=res_id or False)

        attachments = []
        # Add report in attachments
        if template.report_template:
            report_name = self.render_template(template.report_name, template.model, res_id)
            report_service = 'report.' + report_xml_pool.browse(template.report_template.id).report_name
            # Ensure report is rendered using template's language
            ctx = context.copy()
            if template.lang:
                ctx['lang'] = self.render_template(template.lang, template.model, res_id)
            service = netsvc.LocalService(report_service)
            (result, format) = service.create([res_id], {'model': template.model}, ctx)
            result = base64.b64encode(result)
            if not report_name:
                report_name = report_service
            ext = "." + format
            if not report_name.endswith(ext):
                report_name += ext
            attachments.append((report_name, result))

        attachment_ids = []
        # Add template attachments
        for attach in template.attachment_ids:
            attachment_ids.append(attach.id)

        values['attachments'] = attachments
        values['attachment_ids'] = attachment_ids
        return values
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
