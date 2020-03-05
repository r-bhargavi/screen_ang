# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo import SUPERUSER_ID

        
# class sale_shop(osv.osv):
#     _inherit = "sale.shop"
#
#     def _validate_zone_branch(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         record = self.browse(cr, uid, ids, context=context)
#         for data in record:
#             if data.flg_main_branch_zone:
#                 searchids = self.pool.get('sale.shop').search(cr, uid, [('zone_id','=',data.zone_id.id),('id','!=',data.id),('flg_main_branch_zone','=',True)])
#                 if len(searchids) > 0:
#                     return False
#         return True
#
#     def _validate_state_branch(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         record = self.browse(cr, uid, ids, context=context)
#         for data in record:
#             if data.flg_main_branch_state:
#                 zoneids = self.pool.get('state.zone').search(cr, uid, [('state_id','=',data.zone_id.state_id.id)])
#                 searchids = self.pool.get('sale.shop').search(cr, uid, [('zone_id','in',zoneids),('id','!=',data.id),('flg_main_branch_state','=',True)])
#                 if len(searchids) > 0:
#                     return False
#         return True
#
#     def onchange_main_ho_branch(self, cr, uid, ids, flg_main_branch, zone_id, context=None):
#         res={}
#         if flg_main_branch:
#             res['zone_id'] = False
#         return {'value':res}
#
#
#     def _get_state_id(self, cr, uid, ids, context=None):
#         res = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             state_id = False
#             if line.zone_id:
#                 state_id = line.zone_id.state_id.id
#             res[line.id] = state_id
#         return res
#
#
#     _columns = {
#         'zone_id': fields.many2one('state.zone', 'Zone', required=True),
#         'rel_state_id':fields.many2one('res.country.state', 'State'),
#         'ho_branch_id':fields.many2one('sale.shop','HO Branch ID'),
#         'name': fields.char('Branch Name', size=64, required=True),
#         'code':fields.char('Branch Code', size=4, required=True),
#         'flg_main_branch':fields.boolean('Main HO Branch'),
#         'flg_main_branch_zone':fields.boolean('Zone Main Branch'),
#         'flg_main_branch_state':fields.boolean('State Main Branch'),
#         'sequence_id': fields.many2one('ir.sequence', 'Entry Sequence', help="This field contains the information related to the numbering of the Branch wise Case Sheet of this journal.", required=True),
#         'partner_id':fields.many2one('res.partner','Related partner'),
#         'street':fields.related('partner_id','street',type='char', size=128, string='Street'),
#         'street2':fields.related('partner_id','street2',type='char',size=128, string='Street2'),
#         'city':fields.related('partner_id','city',type='char',size=128, string='City'),
#         'state_id':fields.related('partner_id','state_id',type='many2one',relation='res.country.state',string='State'),
#         'zip':fields.related('partner_id','zip',type='char',size=24, string='Pin'),
#         'country_id':fields.related('partner_id','country_id',type='many2one',relation='res.country',string='Country'),
#         'phone':fields.related('partner_id','phone',type='char',size=64, string='Phone', required=True),
#         'location':fields.related('partner_id','client_branch',type='char',size=64, string='Location'),
#     }
#     _constraints = [
#         (_validate_zone_branch, 'Error! Only one Main Branch for a ZONE is Allowed.', ['Zone Main Branch']),
#         (_validate_state_branch, 'Error! Only one Main Branch for a STATE is Allowed.', ['State Main Branch'])
#     ]
#
#     def create_sequence(self, cr, uid, vals, context=None):
#         """ Create new no_gap entry sequence for every new Branch
#         """
#         seq = {
#             'name': vals['name'],
#             'implementation':'no_gap',
#             'padding': 8,
#             'number_increment': 1
#         }
#         if 'company_id' in vals:
#             seq['company_id'] = vals['company_id']
#         return self.pool.get('ir.sequence').create(cr, uid, seq)
#
#     def create(self, cr, uid, vals, context=None):
#         if not 'sequence_id' in vals or not vals['sequence_id']:
#             # if we have the right to create a Branch, we should be able to
#             # create it's sequence.
#             vals.update({'sequence_id': self.create_sequence(cr, SUPERUSER_ID, vals, context)})
#         zone=False
#         if vals.has_key('zone_id') and vals['zone_id']:
#             zone = self.pool.get('state.zone').browse(cr, uid, vals['zone_id'], context=context)
#             vals['rel_state_id'] = (zone.state_id and zone.state_id.id or False)
#             vals['ho_branch_id'] = (zone.state_id and zone.state_id.ho_branch_id and zone.state_id.ho_branch_id.id or False or False)
#         if vals.has_key('partner_id') and not vals['partner_id']:
#             partner_id = self.pool.get('res.partner').create(cr, uid, {'name':vals['name'],'is_company':True,'client_data_id':vals['code'],'phone':vals['phone'],'street':vals['street'],'street2':vals['street2'], 'city':vals['location'], 'client_branch':vals['location'], 'state_id':zone and zone.state_id.id or False,'country_id':zone and zone.state_id.country_id.id or False})
#             vals['partner_id'] = partner_id
#         return super(sale_shop, self).create(cr, uid, vals, context)
#
#     def write(self, cr, uid, ids, vals, context=None):
#         obj = self.browse(cr, uid, ids[0],context=context)
#         if vals.has_key('phone') and not obj.partner_id:
#             partner_id = self.pool.get('res.partner').create(cr, uid, {'name':obj.name,'is_company':True,'client_data_id':obj.code,'phone':vals['phone'],'street':(vals.has_key('street') and vals['street'] or False),'street2':(vals.has_key('street2') and vals['street2'] or False), 'city':(vals.has_key('location') and vals['location'] or False), 'client_branch':(vals.has_key('location') and vals['location'] or False), 'state_id':(obj.zone_id and obj.zone_id.state_id.id or False),'country_id':(obj.zone_id and obj.zone_id.state_id.country_id.id or False)})
#             vals['partner_id'] = partner_id
#         vals['rel_state_id'] = (obj.zone_id and obj.zone_id.state_id.id or False)
#         vals['ho_branch_id'] = (obj.zone_id and obj.zone_id.state_id and obj.zone.state_id.ho_branch_id and obj.zone.state_id.ho_branch_id.id or False or False)
#         retvals = super(sale_shop, self).write(cr, uid, ids, vals, context=context)
#         return retvals
#
# sale_shop()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
