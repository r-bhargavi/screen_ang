# # -*- coding: utf-8 -*-
# import time
# from odoo import fields, models, api
# from openerp.osv.orm import browse_record, browse_null
# from openerp.tools.translate import _
#
# class purchase_requisition_partner(osv.osv_memory):
#     _inherit = "purchase.requisition.partner"
#     _description = "Purchase Requisition Partner"
#
#     _columns = {
#                 'purchase_requisition_line_ids' : fields.one2many('purchase.requisition.partner.line','wizard_id','Products'),
#                 #'hide_tracking': fields.function(_hide_tracking, string='Tracking', type='boolean', help='This field is for internal purpose. It is used to decide if the column production lot has to be shown on the moves or not.'),
#         }
#
#     def default_get(self, cr, uid, fields, context=None):
#         if context is None: context = {}
#         res = super(purchase_requisition_partner, self).default_get(cr, uid, fields, context=context)
#         order_ids = context.get('active_ids', [])
#         active_model = context.get('active_model')
#         if not order_ids or len(order_ids) != 1:
#             return res
#         order_id, = order_ids
#         if 'purchase_requisition_line_ids' in fields:
#             order_obj = self.pool.get('purchase.requisition').browse(cr, uid, order_id, context=context)
#             products = [self._load_avial_products(cr, uid, m) for m in order_obj.line_ids if not m.select]
#             res.update(purchase_requisition_line_ids=products)
#         return res
#
#     def _load_avial_products(self, cr, uid, line):
#         data = {
#             'product_id' : line.product_id.id,
#             #'select':  False,
#             'line_id': line.id,
#             }
#         return data
#
#
#     def create_order(self, cr, uid, ids, context=None):
#         #res = super(purchase_requisition_partner, self).create_order(cr, uid, fields, context=context)
#         active_ids = context and context.get('active_ids', [])
#         data =  self.browse(cr, uid, ids, context=context)[0]
#         if data.purchase_requisition_line_ids:
#             lines = [line.line_id.id for line in data.purchase_requisition_line_ids]
#             purchase_requisition_line_pool = self.pool.get('purchase.requisition.line')
#             for item in data.purchase_requisition_line_ids:
#                 purchase_requisition_line_pool.write(cr, uid,item.line_id.id, {'select':True}, context=context)
#             self.make_purchase_order(cr, uid, active_ids, data.partner_id.id, lines, context=context)
#             return {'type': 'ir.actions.act_window_close'}
#
#
#     def make_purchase_order(self, cr, uid, ids, partner_id, requisition_lines, context=None):
#         """
#         Create New RFQ for Supplier
#         """
#         if context is None:
#             context = {}
#         assert partner_id, 'Supplier should be specified'
#         purchase_order = self.pool.get('purchase.order')
#         purchase_order_line = self.pool.get('purchase.order.line')
#         purchase_requisition_pool = self.pool.get('purchase.requisition')
#         res_partner = self.pool.get('res.partner')
#         fiscal_position = self.pool.get('account.fiscal.position')
#         supplier = res_partner.browse(cr, uid, partner_id, context=context)
#         supplier_pricelist = supplier.property_product_pricelist_purchase or False
#         res = {}
#         for requisition in purchase_requisition_pool.browse(cr, uid, ids, context=context):
#             if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
#                  raise osv.except_osv(_('Warning!'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)
#             location_id = requisition.warehouse_id.lot_input_id.id
#             purchase_id = purchase_order.create(cr, uid, {
#                         'origin': requisition.name,
#                         'partner_id': supplier.id,
#                         'pricelist_id': supplier_pricelist.id,
#                         'location_id': location_id,
#                         'company_id': requisition.company_id.id,
#                         'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
#                         'requisition_id':requisition.id,
#                         'notes':requisition.description,
#                         'warehouse_id':requisition.warehouse_id.id ,
#             })
#             res[requisition.id] = purchase_id
#             for line in requisition.line_ids:
#                 if line.select and line.id in requisition_lines:
#                     product = line.product_id
#                     seller_price, qty, default_uom_po_id, date_planned = purchase_requisition_pool._seller_details(cr, uid, line, supplier, context=context)
#                     taxes_ids = product.supplier_taxes_id
#                     taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
#                     purchase_order_line.create(cr, uid, {
#                         'order_id': purchase_id,
#                         'name': product.partner_ref,
#                         'product_qty': qty,
#                         'product_id': product.id,
#                         'product_uom': default_uom_po_id,
#                         'price_unit': seller_price,
#                         'date_planned': date_planned,
#                         'taxes_id': [(6, 0, taxes)],
#                     }, context=context)
#
#         return res
#
# purchase_requisition_partner()
#
#
# class purchase_requisition_partner_line(osv.TransientModel):
#     _name = "purchase.requisition.partner.line"
#     _rec_name = 'product_id'
#     _columns = {
#         'product_id' : fields.many2one('product.product', string="Products", required=True, ondelete='CASCADE'),
#         #'select': fields.boolean('Select'),
#         'line_id': fields.many2one('purchase.requisition.line', 'Line'),
#         'wizard_id' : fields.many2one('purchase.requisition.partner', string="Wizard", ondelete='CASCADE'),
#         #'tracking': fields.function(_tracking, string='Tracking', type='boolean'),
#     }
#
# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
