# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _

class SplitProducts(models.TransientModel):
    _name = "split.products"

    template_ids = fields.Many2many('product.template', string="Products")

    def _get_attributes_id(self):
        AttributeObj = self.env['product.attribute']
        attribute_color_id = AttributeObj.search([('name', '=', 'Vendor Color')], limit=1)
        attribute_vcolor_id = AttributeObj.search([('name', '=', 'Vendor Color Code')], limit=1)
        attribute_size_id = AttributeObj.search([('name', '=', 'Size')], limit=1)
        return attribute_color_id, attribute_vcolor_id, attribute_size_id

    def _remove_duplicated_sellers(self, template):
        exist_seller = []
        for seller in sorted(template.seller_ids, key=lambda a: a.id, reverse=True):
            if seller.name.id not in exist_seller:
                exist_seller.append(seller.name.id)
            else:
                seller.unlink()
        return True

    def _get_default_code(self, template, product):
        default_code = ''
        if (template.default_code and template.default_code != '') or (product.default_code and product.default_code != ''):
            default_code = template.default_code or product.default_code
            if len(default_code) < len(product.default_code):
                default_code = product.default_code
            if template.attribute_line_ids:
                vendorcolorcode = template.attribute_line_ids.filtered(lambda x: (((x.attribute_id.name).lower()).replace(' ', '')) == 'vendorcolorcode')
                vendorcolor = template.attribute_line_ids.filtered(lambda x: (((x.attribute_id.name).lower()).replace(' ', '')) in ['vendorcolor', 'color'])
                code1 = ''
                code2 = ''
                if vendorcolorcode and vendorcolorcode[0].value_ids:
                    code1 = '-' + vendorcolorcode[0].value_ids[0].name
                    code2 = vendorcolorcode[0].value_ids[0].name
                elif vendorcolor and vendorcolor[0].value_ids:
                    code1 = '-' + vendorcolor[0].value_ids[0].name.replace(" ", "")[:3]
                    code2 = vendorcolor[0].value_ids[0].name.replace(" ", "")[:3]
                if code1 in default_code:
                    code1 = code1 + '.*'
                    default_code = re.sub(code1, "", default_code)
                    return default_code
                elif (code1).upper() in default_code:
                    code1 = code1 + '.*'
                    code1 = (code1).upper()
                    default_code = re.sub(code1, "", default_code)
                    return default_code
                elif code2 in default_code:
                    code2 = code2 + '.*'
                    default_code = re.sub(code2, "", default_code)
                    return default_code
                elif (code2).upper() in default_code:
                    code2 = code2 + '.*'
                    code2 = (code2).upper()
                    default_code = re.sub(code2, "", default_code)
                    return default_code
        return default_code

    def _update_default_code(self):
        # attribute_color_id, attribute_vcolor_id, attribute_size_id = self._get_attributes_id()
        ResPartner = self.env['res.partner']
        products = self.env['product.product'].search([])
        leng = len(products)
        undefined_vendor = ResPartner.search([('name', '=', 'undefined')], limit=1)
        if not undefined_vendor:
            undefined_vendor = ResPartner.create({'name': 'undefined'})
        for product in products:
            leng -= 1
            self._remove_duplicated_sellers(product.product_tmpl_id)
            product_code = ''
            product_name = ''
            if product.seller_ids:
                vendor = product.seller_ids[0]
                if vendor.product_code:
                    product_code = vendor.product_code
                else:
                    product_code = self._get_default_code(product.product_tmpl_id, product)
                    if not product_code or product_code == '':
                        product_code = 'undefined'
                product_name = vendor.product_name if vendor.product_name else product.name
                product.seller_ids = [(1, vendor.id, {'product_code': product_code, 'product_name': product_name})]
            else:
                product_code = self._get_default_code(product.product_tmpl_id, product)
                if not product_code or product_code == '':
                    product_code = 'undefined'
                product_name = product.name if product.name else 'undefined'
                product.seller_ids = [(0, 0, {'name': undefined_vendor.id, 'product_code': product_code, 'product_name': product_name})]
        return True

    def _clear_data(self):
        attribute_color_id, attribute_vcolor_id, attribute_size_id = self._get_attributes_id()
        for template in self.env['product.template'].search([('default_code', '=', '')]):
            if template.product_variant_ids:
                all_code = template.product_variant_ids.mapped('default_code')
                all_code = filter(bool, all_code)
                default_code = all_code[0] or ''
                vendorcolor = template.product_variant_ids[0].attribute_value_ids.filtered(lambda x: x.attribute_id.id == attribute_color_id.id)
                vendorcolorcode = template.product_variant_ids[0].attribute_value_ids.filtered(lambda x: x.attribute_id.id == attribute_vcolor_id.id)
                size = template.product_variant_ids[0].attribute_value_ids.filtered(lambda x: x.attribute_id.id == attribute_size_id.id)
                if vendorcolor and vendorcolor.name:
                    vv = '-' + vendorcolor.name
                    default_code.replace(vv, '')
                if vendorcolorcode and vendorcolorcode.name:
                    vv = '-' + vendorcolorcode.name
                    default_code.replace(vv, '')
                if vendorcolorcode and size.name:
                    vv = '-' + re.sub('[^A-Za-z0-9]+', '', size.name)
                    default_code.replace(vv, '')
                if template.seller_ids:
                    template.seller_ids.write({'product_code': default_code})
        return True

    @api.model
    def default_get(self, fields):
        res = super(SplitProducts, self).default_get(fields)
        template_ids = []
        attribute_color_id, attribute_vcolor_id, attribute_size_id = self._get_attributes_id()
        for line in self.env['product.attribute.line'].search([('attribute_id', '=', attribute_color_id.id)]):
            if len(line.value_ids.ids) > 1 and len(template_ids) != 200:
                if line.product_tmpl_id.id not in template_ids:
                    template_ids.append(line.product_tmpl_id.id)
        res['template_ids'] = template_ids
        return res

    def _create_template(self, oldtemplate, attribute, value):
        TemplateObj = self.env['product.template']
        ProductSupplierinfo = self.env['product.supplierinfo']
        ProductAttrLine = self.env['product.attribute.line']
        split_temp = TemplateObj.with_context(create_product_product=True).create(
            {
                'name': oldtemplate.name,
                'default_code': oldtemplate.default_code,
                'default_code_dup': oldtemplate.default_code_dup,
                'default_code_global': oldtemplate.default_code_global,
                'categ_id': oldtemplate.categ_id.id,
                'pos_categ_id': oldtemplate.pos_categ_id.id,
                'style': oldtemplate.style,
                'brand_id': oldtemplate.brand_id.id,
                'type': oldtemplate.type,
                'available_in_pos': oldtemplate.available_in_pos,
                'description': oldtemplate.name,  # Unieque existing product template
                'taxes_id': [(6, 0, oldtemplate.taxes_id.ids)],
                'list_price': oldtemplate.list_price,
                'goods_season': oldtemplate.goods_season.id,
                'goods_year': oldtemplate.goods_year.id,
                'standard_price': oldtemplate.standard_price,
                'season_code': oldtemplate.season_code
            })
        split_temp_default_code = split_temp.default_code
        for seller in oldtemplate.seller_ids:
            ProductSupplierinfo.create({
                'name': seller.name.id,
                'price': seller.price,
                'msrp_price': seller.msrp_price,
                'product_code': seller.product_code or split_temp_default_code,
                'product_name': seller.product_name,
                'product_tmpl_id': split_temp.id
            })
            if not seller.product_code:
                seller.product_code = split_temp_default_code
        for attr_line in oldtemplate.attribute_line_ids:
            values = []
            if attr_line.attribute_id.name.lower().replace(' ', '') == 'vendorcolor':
                values = [value.id]
                split_temp_default_code += '-' + self.env['product.attribute.value'].browse(values).name[:3]
            else:
                values = attr_line.value_ids.ids
            if values:
                ProductAttrLine.create({
                    'attribute_id': attr_line.attribute_id.id,
                    'value_ids': [(6, 0, values)],
                    'product_tmpl_id': split_temp.id
                })
        split_temp_default_code = (split_temp_default_code).upper()
        varaint_to_split_new = self.env['product.product']
        for variant in oldtemplate.product_variant_ids:
            size = variant.attribute_value_ids.filtered(lambda x: x.attribute_id.name.lower().replace(' ', '') == 'size')
            if size:
                variant.default_code = oldtemplate.default_code + '-' + re.sub('[^A-Za-z0-9]+', '', size.name)
            if any(a for a in variant.attribute_value_ids.ids if a == value.id):
                varaint_to_split_new |= variant
        for vv in varaint_to_split_new:
            size = vv.attribute_value_ids.filtered(lambda x: x.attribute_id.name.lower().replace(' ', '') == 'size')
            if size:
                vv.write({'product_tmpl_id': split_temp.id, 'default_code': split_temp_default_code + '-' + re.sub('[^A-Za-z0-9]+', '', size.name)})
            vv.write({'product_tmpl_id': split_temp.id, 'default_code': split_temp_default_code})
        return True

    @api.multi
    def split(self):
        attribute_color_id = self.env['product.attribute'].search([('name', '=', 'Vendor Color')], limit=1)
        for template in self.template_ids:
            color_lines = template.attribute_line_ids.filtered(lambda x: x.attribute_id.id == attribute_color_id.id)
            first_value = color_lines.mapped('value_ids')[0]
            for color in color_lines.mapped('value_ids') - first_value:
                self._create_template(template, attribute_color_id, color)
            color_lines.write({'value_ids': [(6, 0, first_value.ids)]})
        return True

    @api.multi
    def clear_data(self):
        self._clear_data()
        return True

    @api.multi
    def update_inter_ref(self):
        self._update_default_code()
        return True
