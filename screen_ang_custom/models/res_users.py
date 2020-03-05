# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import SUPERUSER_ID


class ResUsers(models.Model):
    _inherit = 'res.users'

    location_ids=fields.Many2many('ho.branch', 'res_location_users_rel', 'user_id', 'location_id','Allowed Locations')
    work_email = fields.Char('Work Email')
    ho_branch_id = fields.Many2one('ho.branch', 'Office')


    @api.model
    def create(self, vals):
        gids = self.env['res.groups'].search([('name', '=', 'Associate'), ('category_id', '=', False)])
        gstring = False
        if len(gids):
            if ('in_group_' + str(gids[0])) in vals and vals['in_group_' + str(gids[0])]:
                gstring = True

        user_id = super(ResUsers, self).create(vals)
        if user_id:
            # self.env['hr.employee'].create({'name': user_id.name,
            #                                 'user_id': user_id.id,
            #                                 'work_email': user_id.work_email,
            #                                 'ho_branch_id': user_id.ho_branch_id.id,
            #                                 'address_home_id': user_id.partner_id.id})
            self.env['hr.employee'].create({'name': user_id['name'],
                                            'user_id': user_id['id'],
                                            'work_email': user_id['work_email'],
                                            'ho_branch_id': user_id['ho_branch_id'].id,
                                            'address_home_id': user_id['partner_id'].id})
        user = self.browse(user_id)
        if user_id.partner_id and gstring:
            user_id.partner_id.write({'supplier': True})
        elif user_id.partner_id and not gstring:
            user_id.partner_id.write({'supplier': False})
        return user_id


    @api.multi
    def write(self, values):
        gids = self.env['res.groups'].search([('name', '=', 'Associate'), ('category_id', '=', False)])
        gstring = False
        ids=self.ids
        if len(gids):
            # if values.has_key('in_group_' + str(gids[0])) and values['in_group_' + str(gids[0])]:
            if ('in_group_' + str(gids[0])) in values and values['in_group_' + str(gids[0])]:
                gstring = True

        if values.get('password', False):
            uid = SUPERUSER_ID
        res = super(ResUsers, self).write(values)
        if not isinstance(self.ids, (list)):
            ids = [self.ids]
        for user in self:
            if user.partner_id and gstring:
                user.partner_id.write({'supplier': True})
            elif user.partner_id and not gstring:
                user.partner_id.write({'supplier': False})

        return res