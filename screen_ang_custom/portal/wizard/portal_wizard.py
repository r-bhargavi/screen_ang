# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class Wizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of portal users.
    """
    _inherit = 'portal.wizard'
    _description = 'Portal Access Management'

    @api.onchange('portal_id')
    def onchange_portal_id(self):
        # for each partner, determine corresponding portal.wizard.user records
        res_partner = self.env['res.partner']
        partner_ids =self._context.get('active_ids') or []
        contact_ids = set()
        user_changes = []
        for partner in res_partner.browse(SUPERUSER_ID, partner_ids):
            for contact in ([partner]):
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    in_portal = False
                    if contact.user_ids:
                        in_portal = self.portal_id in [g.id for g in contact.user_ids[0].groups_id]
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'email': contact.email,
                        'in_portal': in_portal,
                    }))
        for partner in res_partner.browse(SUPERUSER_ID, partner_ids):
            for contact in (partner.child_ids):
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    in_portal = False
                    if contact.user_ids:
                        in_portal = self.portal_id in [g.id for g in contact.user_ids[0].groups_id]
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'email': contact.email,
                        'in_portal': in_portal,
                    }))
        return {'value': {'user_ids': user_changes}}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: