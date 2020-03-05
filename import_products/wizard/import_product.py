# -*- coding: utf-8 -*-
import io
import os
import re
import csv
import logging
import base64
from odoo import fields, models, _
from odoo.tools import pycompat

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

_logger = logging.getLogger(__name__)

class ImportProducts(models.TransientModel):
    _name = "import.products"

    file_path = fields.Binary(type='binary', string="File To Import")

    def _read_csv_data(self, binary_data):
        """ Reads CSV from given path and Return list of dict with Mapping """
        data = csv.reader(StringIO(base64.b64decode(binary_data).decode('utf-8', 'ignore')), quotechar='"', delimiter=',')
        # Read the column names from the first line of the file
        fields = next(data)
        data_lines = []
        for row in data:
            items = dict(zip(fields, row))
            data_lines.append(items)
        return fields, data_lines

    def _write_bounced_file(self, bounced_detail, ftype):
        try:
            fecfile = io.BytesIO()
            w = pycompat.csv_writer(fecfile, delimiter='|')
            if ftype == 'web_categ':
                w.writerow(bounced_detail[0].keys())
                for dt in bounced_detail:
                    w.writerow(dt.values())
            else:
                for dt in bounced_detail:
                    w.writerow(dt)
            return fecfile
        except Exception:
            _logger.warning("Can not Export bounced(Rejected) quotation detail to the file. ")
            return False

    def _get_bounced_url(self, fecfile, fname):
        fecvalue = fecfile.getvalue()
        base_url = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value
        attachment_id = self.env['ir.attachment'].create({
            'name': fname,
            'datas': base64.encodestring(fecvalue),
            'datas_fname': fname,
            })
        url = str(base_url)+'/web/content/'+str(attachment_id.id)+'?download=true'
        return url

    def _remove_ascill_char(self, value):
        return re.sub(r'[^\x00-\x7F]+', '', value).strip()

    def _get_attribute_value(self, domain):
        return self.env['product.attribute.value'].search(domain)

    def _create_attribute_value(self, vals):
        return self.env['product.attribute.value'].create(vals)

    def do_import_product_data(self):
        data = self.read()[0]
        file_path = data['file_path']  # import data from binary field
        if not file_path or file_path == "":
            _logger.warning("Import can not be started. Configure your schedule Actions.")
            return True
        fields = data_lines = False
        fields, data_lines = self._read_csv_data(file_path)
        try:
            fields, data_lines = self._read_csv_data(file_path)
        except:
            _logger.warning("Can not read source file(csv) '%s', Invalid file path or File not reachable on file system." % (file_path))
            return True
        if not data_lines:
            _logger.info("File '%s' has no data or it has been already imported, please update the file." % (file_path))
            return True
        _logger.info("Starting Import Product Process from file '%s'." % (file_path))

        product_tmpl_obj = self.env['product.template']
        Product_obj = self.env['product.product']
        product_attribute = self.env['product.attribute']
        pos_category_obj = self.env['pos.category']
        ir_model_data_obj = self.env['ir.model.data']
        season_obj = self.env['wws_product.option.season']
        season_year_obj = self.env['wws_product.option.year']
        attribute_value_obj = self.env['product.attribute.value']
        PublicCategory = self.env['product.public.category']
        ProductCategory = self.env['product.category']
        ProductBrand = self.env['product.brand']
        ResPartner = self.env['res.partner']

        bounced_cust = [tuple(fields)]
        error_lst = []
        product_tmpl_id = False

        rem_product_tmpl_desc = []
        record = 1
        main_value_list = {}
        notto_unlink = []
        bounce_categs = []

        # Product Attributes
        attribute_color_id = product_attribute.search([('name', '=', 'Vendor Color')], limit=1)
        attribute_color_code_id = product_attribute.search([('name', '=', 'Vendor Color Code')], limit=1)
        attribute_board_art_id = product_attribute.search([('name', '=', 'Board Art')], limit=1)
        attribute_size_id = product_attribute.search([('name', '=', 'Size')], limit=1)
        attribute_fins_id = product_attribute.search([('name', '=', 'Fins')], limit=1)
        attribute_width_id = product_attribute.search([('name', '=', 'Width')], limit=1)
        attribute_thickness_id = product_attribute.search([('name', '=', 'Thickness')], limit=1)
        attribute_volume_id = product_attribute.search([('name', '=', 'Volume')], limit=1)
        attribute_lens_color_id = product_attribute.search([('name', '=', 'Lens Color')], limit=1)
        attribute_size_inseam_id = product_attribute.search([('name', '=', 'Inseam')], limit=1)
        attribute_finish_id = product_attribute.search([('name', '=', 'Finish')], limit=1)
        attribute_tail_shape_id = product_attribute.search([('name', '=', 'Tail Shape')], limit=1)
        attribute_core_material_id = product_attribute.search([('name', '=', 'Core Material')], limit=1)
        attribute_resin_type_id = product_attribute.search([('name', '=', 'Resin Type')], limit=1)

        for data in data_lines:
            categ_id = self._remove_ascill_char(data['Internal Category'])
            pos_categ_id = self._remove_ascill_char(data['POS Category'])
            available_in_pos = self._remove_ascill_char(data['Available in POS'])
            ptype = self._remove_ascill_char(data['Product Type'])
            vendor = self._remove_ascill_char(data['Vendor'])
            brand = self._remove_ascill_char(data['Brand'])
            season_code = self._remove_ascill_char(data['Season'])
            default_code = self._remove_ascill_char(data['Style'])
            style = self._remove_ascill_char(data['Style'])
            description = self._remove_ascill_char(data['Description'])
            standard_price = self._remove_ascill_char(data['W/S'])
            msrp = self._remove_ascill_char(data['MSRP'])
            list_price = self._remove_ascill_char(data['WWRP'])
            upc = self._remove_ascill_char(data['UPC'])
            item_number = self._remove_ascill_char(data['Item #'])

            # Product Attributes Values
            color = self._remove_ascill_char(data['Color'])
            color_code = self._remove_ascill_char(data['Color Code'])
            board_art = self._remove_ascill_char(data['Board Art'])
            lens_color = self._remove_ascill_char(data['Lens Color'])
            size = self._remove_ascill_char(data['Size'])
            width = self._remove_ascill_char(data['Width'])
            thickness = self._remove_ascill_char(data['Thickness'])
            fins = self._remove_ascill_char(data['Fins'])
            finish = self._remove_ascill_char(data['Finish'])
            tail_shape = self._remove_ascill_char(data['Tail Shape'])
            volume = self._remove_ascill_char(data['Volume'])
            resin_type = self._remove_ascill_char(data['Resin Type'])
            size_inseam = self._remove_ascill_char(data['Inseam'])
            core_material = self._remove_ascill_char(data['Core Material'])
            description_sale = self._remove_ascill_char(data['Web Description'])
            public_categs = self._remove_ascill_char(data['Web Category'])
            public_categ_ids = []
            for pub_categ in public_categs.split(';'):
                if pub_categ or pub_categ != '':
                    pub_category = PublicCategory.search([('name', '=', pub_categ)], limit=1)
                    if pub_category:
                        public_categ_ids.append(pub_category.id)
                    else:
                        bounce_categs.append({'Item #': item_number, 'Product': description, 'Web Category': pub_categ, 'Reason': 'Category Not Found'})

            external_internal_categ_id = False
            external_pos_categ_id = False
            if categ_id:
                external_internal_categ_id = ir_model_data_obj.search([('name', '=', categ_id.split('.')[1]), ('model', '=', 'product.category')], limit=1)
                pos_categ = categ_id.split('.')[1].replace('product_category', 'pos_category')
                external_pos_categ_id = ir_model_data_obj.search([('name', '=', pos_categ), ('model', '=', 'pos.category')], limit=1)

            if season_code:
                season_id = season_obj.search([('abbreviated_code', '=', season_code[-1])], limit=1).id or False
                season_year_id = season_year_obj.search([('abbreviated_code', '=', season_code[:-1])], limit=1).id or False
            else:
                season_id = False
                season_year_id = False

            if color:
                attribute_color_value_id = self._get_attribute_value([('name', '=', color), ('attribute_id', '=', attribute_color_id.id)])
            else:
                attribute_color_value_id = False

            if color_code:
                attribute_color_code_value_id = self._get_attribute_value([('name', '=', color_code), ('attribute_id', '=', attribute_color_code_id.id)])
            else:
                attribute_color_code_value_id = False

            if board_art:
                attribute_board_art_value_id = self._get_attribute_value([('name', '=', board_art), ('attribute_id', '=', attribute_board_art_id.id)])
            else:
                attribute_board_art_value_id = False

            if size:
                attribute_size_value_id = self._get_attribute_value([('name', '=', size), ('attribute_id', '=', attribute_size_id.id)])
                if attribute_size_value_id and not self.env['merge.attribute.value'].search([('dest_value', '=', attribute_size_value_id.id)]):
                    self.env.cr.execute("""SELECT merge_attribute_value_id FROM merge_attribute_value_product_attribute_value_rel WHERE product_attribute_value_id=%s""", (attribute_size_value_id.id,))
                    results = self.env.cr.fetchone()
                    if results:
                        attribute_size_value_id = self.env['merge.attribute.value'].browse(results[0]).dest_value
            else:
                attribute_size_value_id = False

            if fins:
                attribute_fins_value_id = self._get_attribute_value([('name', '=', fins), ('attribute_id', '=', attribute_fins_id.id)])
            else:
                attribute_fins_value_id = False

            if width:
                attribute_width_value_id = self._get_attribute_value([('name', '=', width), ('attribute_id', '=', attribute_width_id.id)])
            else:
                attribute_width_value_id = False

            if thickness:
                attribute_thickness_value_id = self._get_attribute_value([('name', '=', thickness), ('attribute_id', '=', attribute_thickness_id.id)])
            else:
                attribute_thickness_value_id = False

            if volume:
                attribute_volume_value_id = self._get_attribute_value([('name', '=', volume), ('attribute_id', '=', attribute_volume_id.id)])  # , ('wws_code', '=', color_code)
            else:
                attribute_volume_value_id = False

            if lens_color:
                attribute_lens_color_value_id = self._get_attribute_value([('name', '=', lens_color), ('attribute_id', '=', attribute_lens_color_id.id)])
            else:
                attribute_lens_color_value_id = False

            if size_inseam:
                attribute_size_inseam_value_id = self._get_attribute_value([('name', '=', size_inseam), ('attribute_id', '=', attribute_size_inseam_id.id)])
            else:
                attribute_size_inseam_value_id = False

            if finish:
                attribute_finish_value_id = self._get_attribute_value([('name', '=', finish), ('attribute_id', '=', attribute_finish_id.id)])
            else:
                attribute_finish_value_id = False

            if tail_shape:
                attribute_tail_shape_value_id = self._get_attribute_value([('name', '=', tail_shape), ('attribute_id', '=', attribute_tail_shape_id.id)])
            else:
                attribute_tail_shape_value_id = False

            if core_material:
                attribute_core_material_value_id = self._get_attribute_value([('name', '=', core_material), ('attribute_id', '=', attribute_core_material_id.id)])
            else:
                attribute_core_material_value_id = False

            if resin_type:
                attribute_resin_type_value_id = self._get_attribute_value([('name', '=', resin_type), ('attribute_id', '=', attribute_resin_type_id.id)])
            else:
                attribute_resin_type_value_id = False

            internal_categ_id = external_internal_categ_id.res_id if external_internal_categ_id else False
            pos_categ_id = external_pos_categ_id.res_id if external_pos_categ_id else False
            if not external_pos_categ_id and external_internal_categ_id:
                pos_categ_list = external_internal_categ_id.display_name.split(' / ')
                last_categ = pos_categ_list.pop()
                if 'All' in pos_categ_list:
                    pos_categ_list.remove('All')
                if 'Saleable' in pos_categ_list:
                    pos_categ_list.remove('Saleable')

                parent_id = False
                for l in pos_categ_list:
                    if not parent_id:
                        pos_categ_id = pos_category_obj.search([('name', '=', l)])
                        parent_id = pos_categ_id.id
                    else:
                        pos_categ_id = pos_category_obj.search([('name', '=', l), ('parent_id', '=', parent_id)])
                        parent_id = pos_categ_id.id
                if pos_categ_id.name != last_categ:
                    pos_categ_id = pos_category_obj.create({'name': last_categ, 'parent_id': pos_categ_id.id})
                    ir_model_data_obj.create({'module': 'wws', 'name': pos_categ, 'model': 'pos.category', 'res_id': pos_categ_id.id})
                pos_categ_id = pos_categ_id.id if pos_categ_id else False

            brand_id = ProductBrand.search([('name', '=', brand)], limit=1)
            vendor_id = ResPartner.search([('name', '=ilike', vendor)], limit=1)

            if not attribute_color_value_id and color:
                attribute_color_value_id = self._create_attribute_value({'attribute_id': attribute_color_id.id, 'name': color})

            if not attribute_color_code_value_id and color_code:
                attribute_color_code_value_id = self._create_attribute_value({'attribute_id': attribute_color_code_id.id, 'name': color_code})

            if not attribute_board_art_value_id and board_art:
                attribute_board_art_value_id = self._create_attribute_value({'attribute_id': attribute_board_art_id.id, 'name': board_art})

            if not attribute_size_value_id and size:
                attribute_size_value_id = self._create_attribute_value({'attribute_id': attribute_size_id.id, 'name': size})

            if not attribute_fins_value_id and fins:
                attribute_fins_value_id = self._create_attribute_value({'attribute_id': attribute_fins_id.id, 'name': fins})

            if not attribute_width_value_id and width:
                attribute_width_value_id = self._create_attribute_value({'attribute_id': attribute_width_id.id, 'name': width})

            if not attribute_thickness_value_id and thickness:
                attribute_thickness_value_id = self._create_attribute_value({'attribute_id': attribute_thickness_id.id, 'name': thickness})

            if not attribute_volume_value_id and volume:
                attribute_volume_value_id = self._create_attribute_value({'attribute_id': attribute_volume_id.id, 'name': volume})

            if not attribute_lens_color_value_id and lens_color:
                attribute_lens_color_value_id = self._create_attribute_value({'attribute_id': attribute_lens_color_id.id, 'name': lens_color})

            if not attribute_size_inseam_value_id and size_inseam:
                attribute_size_inseam_value_id = self._create_attribute_value({'attribute_id': attribute_size_inseam_id.id, 'name': size_inseam})

            if not attribute_finish_value_id and finish:
                attribute_finish_value_id = self._create_attribute_value({'attribute_id': attribute_finish_id.id, 'name': finish})

            if not attribute_tail_shape_value_id and tail_shape:
                attribute_tail_shape_value_id = self._create_attribute_value({'attribute_id': attribute_tail_shape_id.id, 'name': tail_shape})

            if not attribute_core_material_value_id and core_material:
                attribute_core_material_value_id = self._create_attribute_value({'attribute_id': attribute_core_material_id.id, 'name': core_material})

            if not attribute_resin_type_value_id and resin_type:
                attribute_resin_type_value_id = self._create_attribute_value({'attribute_id': attribute_resin_type_id.id, 'name': resin_type})

            attribute_value_list = []
            attribute_line_ids = []
            if attribute_size_value_id:
                attribute_value_list.append(attribute_size_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_size_value_id.attribute_id.id, 'value_ids': attribute_size_value_id.ids}))
            if attribute_width_value_id:
                attribute_value_list.append(attribute_width_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_width_value_id.attribute_id.id, 'value_ids': attribute_width_value_id.ids}))
            if attribute_thickness_value_id:
                attribute_value_list.append(attribute_thickness_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_thickness_value_id.attribute_id.id, 'value_ids': attribute_thickness_value_id.ids}))
            if attribute_volume_value_id:
                attribute_value_list.append(attribute_volume_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_volume_value_id.attribute_id.id, 'value_ids': attribute_volume_value_id.ids}))
            if attribute_fins_value_id:
                attribute_value_list.append(attribute_fins_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_fins_value_id.attribute_id.id, 'value_ids': attribute_fins_value_id.ids}))
            if attribute_tail_shape_value_id:
                attribute_value_list.append(attribute_tail_shape_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_tail_shape_value_id.attribute_id.id, 'value_ids': attribute_tail_shape_value_id.ids}))
            if attribute_finish_value_id:
                attribute_value_list.append(attribute_finish_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_finish_value_id.attribute_id.id, 'value_ids': attribute_finish_value_id.ids}))
            if attribute_color_value_id:
                attribute_value_list.append(attribute_color_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_color_value_id.attribute_id.id, 'value_ids': attribute_color_value_id.ids}))
            if attribute_color_code_value_id:
                attribute_value_list.append(attribute_color_code_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_color_code_value_id.attribute_id.id, 'value_ids': attribute_color_code_value_id.ids}))
            if attribute_board_art_value_id:
                attribute_value_list.append(attribute_board_art_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_board_art_value_id.attribute_id.id, 'value_ids': attribute_board_art_value_id.ids}))
            if attribute_lens_color_value_id:
                attribute_value_list.append(attribute_lens_color_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_lens_color_value_id.attribute_id.id, 'value_ids': attribute_lens_color_value_id.ids}))
            if attribute_resin_type_value_id:
                attribute_value_list.append(attribute_resin_type_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_resin_type_value_id.attribute_id.id, 'value_ids': attribute_resin_type_value_id.ids}))
            if attribute_core_material_value_id:
                attribute_value_list.append(attribute_core_material_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_core_material_value_id.attribute_id.id, 'value_ids': attribute_core_material_value_id.ids}))
            if attribute_size_inseam_value_id:
                attribute_value_list.append(attribute_size_inseam_value_id.id)
                attribute_line_ids.append((0, 0, {'attribute_id': attribute_size_inseam_value_id.attribute_id.id, 'value_ids': attribute_size_inseam_value_id.ids}))

            name = ''
            name += re.sub(r'[^\x00-\x7F]+', '', default_code) if default_code else ''
            name += '-' if color_code else ''
            name += color_code if color_code else ''
            product_default_code = re.sub(r'[^\x00-\x7F]+', '', style) if style else ''
            template_default_code = product_default_code
            if attribute_value_list:
                attribute_list = attribute_value_obj.browse(attribute_value_list)
                vendor_color_code = attribute_list.filtered(lambda self: (((self.attribute_id.name).lower()).replace(' ', '')) == 'vendorcolorcode')
                vendor_color = attribute_list.filtered(lambda self: (((self.attribute_id.name).lower()).replace(' ', '')) == 'vendorcolor')
                size = attribute_list.filtered(lambda x: (((x.attribute_id.name).lower()).replace(' ', '')) == 'size')
                if vendor_color_code:
                    product_default_code += '-' if name else ''
                    product_default_code += (vendor_color_code[0].name) if vendor_color_code[0] else ''
                if not vendor_color_code and vendor_color:
                    product_default_code += '-' if product_default_code else ''
                    product_default_code += (vendor_color[0].name.replace(" ", "")[:3]) if vendor_color[0] else ''
                template_default_code = (product_default_code).upper()
                if size:
                    product_default_code += '-' if product_default_code else ''
                    product_default_code += re.sub('[^A-Za-z0-9]+', '', size[0].name) if size[0] else ''
            name = (name).upper()
            product_default_code = (product_default_code).upper()
            exist_product_template = product_tmpl_obj.search([('brand_id', '=', brand_id.id), '|', ('default_code', '=', template_default_code), ('default_code_dup', '=', template_default_code)])
            product_barcode = False
            if upc:
                upc_search = '0' + str(upc)
                product_barcode = Product_obj.search(['|', ('barcode', '=', upc), ('barcode', '=', upc_search), '|', ('active', '=', True), ('active', '=', False)], limit=1)
            else:
                product_barcode = Product_obj.search([('default_code', '=', product_default_code), '|', ('active', '=', True), ('active', '=', False)], limit=1)
            if len(exist_product_template.ids) != 1:
                exist_product_template_test = product_tmpl_obj.search([('barcode', '=', upc)])
                if not exist_product_template_test and exist_product_template:
                    exist_product_template = exist_product_template[0]
                else:
                    exist_product_template = exist_product_template_test
            if exist_product_template:
                old_list_price = exist_product_template.list_price
                product_tmpl_id = exist_product_template.id
                for attr in attribute_line_ids:
                    exist_attr_line = exist_product_template.attribute_line_ids.filtered(lambda x: x.attribute_id.id == attr[2]['attribute_id'])
                    if not exist_attr_line:
                        self.env['product.attribute.line'].create({
                            'attribute_id': attr[2]['attribute_id'],
                            'value_ids': [(6, 0, attr[2]['value_ids'])],
                            'product_tmpl_id': exist_product_template.id
                        })
                    else:
                        if exist_product_template.id not in main_value_list:
                            main_value_list[exist_product_template.id] = attr[2]['value_ids']
                        else:
                            main_value_list[exist_product_template.id] += attr[2]['value_ids']
                        old_values = list(set(exist_attr_line.value_ids.ids + attr[2]['value_ids']))
                        new_values = [a for a in old_values if a in main_value_list[exist_product_template.id]]
                        if new_values:
                            if exist_attr_line.attribute_id.name.lower().replace(' ', '') == 'vendorcolorcode':
                                if attribute_color_code_value_id:
                                    exist_attr_line.write({'value_ids': [(6, 0, attribute_color_code_value_id.ids)]})
                            elif exist_attr_line.attribute_id.name.lower().replace(' ', '') == 'vendorcolor':
                                if attribute_color_value_id:
                                    exist_attr_line.write({'value_ids': [(6, 0, attribute_color_value_id.ids)]})
                            else:
                                exist_attr_line.write({'value_ids': [((6, 0, new_values))]})
                if product_barcode:
                    product_vals = {
                        'active': True,
                        'name': description if description else exist_product_template.name,
                        'brand_id': exist_product_template.brand_id.id,
                        'product_tmpl_id': product_tmpl_id,
                        'lst_price': list_price if list_price else old_list_price,
                        'attribute_value_ids': [(6, 0, attribute_value_list)],
                        'goods_season': season_id,
                        'goods_year': season_year_id,
                        'season_code': season_code,
                        'default_code': product_default_code,
                        # 'barcode': False if product_barcode else upc,
                        # 'item_number': item_number,
                        # 'msrp': msrp,
                        'standard_price': standard_price if standard_price else 0.0,
                    }
                    product_barcode.write(product_vals)
                    if vendor_id:
                        line = product_barcode.seller_ids.filtered(lambda self: self.name.id == vendor_id.id)
                        if line:
                            line[0].price = standard_price if standard_price else 0.0
                            line[0].msrp_price = msrp if msrp else 0.0
                            line[0].product_code = default_code
                            line[0].product_name = description
                        else:
                            product_barcode.seller_ids = [(0, 0, {'name': vendor_id.id, 'price': standard_price if standard_price else 0.0, 'msrp_price': msrp, 'product_code': default_code, 'product_name': description})]
                    if not product_barcode.product_tmpl_id.default_code:
                        product_barcode.product_tmpl_id.default_code = product_barcode.default_code if product_barcode.default_code else exist_product_template.default_code_global
                    if not product_barcode.product_tmpl_id.goods_season:
                        product_barcode.product_tmpl_id.goods_season = season_id
                    if not product_barcode.product_tmpl_id.goods_year:
                        product_barcode.product_tmpl_id.goods_year = season_year_id
                else:
                    item_number_rec = False
                    if item_number:
                        item_number_rec = Product_obj.search([('item_number', '=', item_number), '|', ('active', '=', True), ('active', '=', False)])
                    if item_number_rec:
                        product_vals = {
                            'active': True,
                            'name': description if description else exist_product_template.name,
                            'brand_id': exist_product_template.brand_id.id,
                            'barcode': upc if upc else False,
                            'item_number': item_number_rec.item_number,
                            'product_tmpl_id': product_tmpl_id,
                            'goods_season': season_id,
                            'goods_year': season_year_id,
                            'season_code': season_code,
                            'lst_price': list_price if list_price else old_list_price,
                            'default_code': product_default_code,
                            # 'default_code': default_code,
                            'standard_price': standard_price if standard_price else 0.0,
                            # 'msrp': msrp
                        }
                        if attribute_value_list:
                            product_vals['attribute_value_ids'] = [(6, 0, attribute_value_list)]
                        item_number_rec.write(product_vals)

                        if vendor_id:
                            line = item_number_rec.seller_ids.filtered(lambda self: self.name.id == vendor_id.id)
                            if line:
                                line[0].price = standard_price if standard_price else 0.0
                                line[0].msrp_price = msrp if msrp else 0.0
                                line[0].product_code = default_code
                                line[0].product_name = description
                            else:
                                item_number_rec.seller_ids = [(0, 0, {'name': vendor_id.id, 'price': standard_price if standard_price else 0.0, 'msrp_price': msrp, 'product_code': default_code, 'product_name': description})]
                        if not item_number_rec.product_tmpl_id.default_code:
                            item_number_rec.product_tmpl_id.default_code = item_number_rec.default_code if item_number_rec.default_code else exist_product_template.default_code_global
                        if not item_number_rec.product_tmpl_id.goods_season:
                            item_number_rec.product_tmpl_id.goods_season = season_id
                        if not item_number_rec.product_tmpl_id.goods_year:
                            item_number_rec.product_tmpl_id.goods_year = season_year_id

                    else:
                        product_vals = {
                            'name': description if description else exist_product_template.name,
                            'brand_id': exist_product_template.brand_id.id,
                            'barcode': upc if upc else False,
                            'product_tmpl_id': product_tmpl_id,
                            'goods_season': season_id,
                            'goods_year': season_year_id,
                            'lst_price': list_price if list_price else old_list_price,
                            'default_code': product_default_code,
                            'season_code': season_code,
                            # 'default_code': default_code,
                            # 'item_number': item_number,
                            'standard_price': standard_price if standard_price else 0.0,
                            # 'msrp': msrp
                        }
                        if attribute_value_list:
                            product_vals['attribute_value_ids'] = [(6, 0, attribute_value_list)]
                        product_id = Product_obj.create(product_vals)
                        notto_unlink.append(product_id.id)
                        if vendor_id:
                            line = product_id.seller_ids.filtered(lambda self: self.name.id == vendor_id.id)
                            if line:
                                line[0].price = standard_price if standard_price else 0.0
                                line[0].msrp_price = msrp if msrp else 0.0
                                line[0].product_code = default_code
                                line[0].product_name = description
                            else:
                                product_id.seller_ids = [(0, 0, {'name': vendor_id.id, 'price': standard_price if standard_price else 0.0, 'msrp_price': msrp, 'product_code': default_code, 'product_name': description})]
                        if not product_id.product_tmpl_id.default_code:
                            product_id.product_tmpl_id.default_code = product_id.default_code if product_id.default_code else exist_product_template.default_code_global
                        if not product_id.product_tmpl_id.goods_season:
                            product_id.product_tmpl_id.goods_season = season_id
                        if not product_id.product_tmpl_id.goods_year:
                            product_id.product_tmpl_id.goods_year = season_year_id
                exist_product_template.write({
                    'default_code': template_default_code,
                    'default_code_dup': name,
                    'season_code': season_code,
                    'goods_season': season_id,
                    'goods_year': season_year_id,
                    'categ_id': internal_categ_id,
                    'lst_price': list_price if list_price else old_list_price,
                    'description_sale': description_sale,
                    'public_categ_ids': [(6, 0, public_categ_ids)]
                })
            else:
                taxes_ids = ProductCategory.browse(internal_categ_id).taxes_id.ids
                product_template_vals = {
                    'name': description,
                    'default_code': template_default_code,
                    'default_code_dup': template_default_code,
                    'default_code_global': name,
                    'categ_id': internal_categ_id,
                    'pos_categ_id': pos_categ_id,
                    'style': style,
                    'brand_id': brand_id.id,
                    'type': ptype if ptype else 'product',
                    'available_in_pos': False if available_in_pos else True,
                    'description': name,  # Unieque existing product template
                    'seller_ids': [(0, 0, {'name': vendor_id.id, 'price': standard_price if standard_price else 0.0, 'msrp_price': msrp, 'product_code': default_code, 'product_name': description})] if vendor_id else False,
                    'taxes_id': [(6, 0, taxes_ids)],
                    'list_price': list_price,
                    'goods_season': season_id,
                    'goods_year': season_year_id,
                    # 'seller_ids': [(0, 0, {'name': vendor_id.id, 'price': 0})] if vendor_id else False,
                    # 'msrp': msrp,
                    'standard_price': standard_price if standard_price else 0.0,
                    'attribute_line_ids': attribute_line_ids,
                    'season_code': season_code,
                    'description_sale': description_sale,
                    'public_categ_ids': [(6, 0, public_categ_ids)]
                }
                if not product_barcode:
                    product_template_vals['barcode'] = upc if upc else False

                if product_barcode:
                    new_template = product_tmpl_obj.with_context(create_product_product=True).create(product_template_vals)
                    product_barcode.write({'product_tmpl_id': new_template.id, 'active': True})
                else:
                    new_attribute_line_ids = attribute_line_ids
                    for attr in new_attribute_line_ids:
                        attr[2].update({'value_ids': [(6, 0, attr[2]['value_ids'])]})
                    new_template = product_tmpl_obj.create(product_template_vals)
                notto_unlink += new_template.product_variant_ids.ids
                rem_product_tmpl_desc.append(new_template)
                product_vals = {
                    # 'item_number': item_number,
                    # 'default_code': default_code,
                    'product_tmpl_id': new_template.id,
                    'goods_season': season_id,
                    'goods_year': season_year_id,
                    'season_code': season_code,
                    'default_code': product_default_code,
                }
                if not product_barcode:
                    product_vals['barcode'] = upc if upc else False
                if attribute_value_list:
                    product_vals['attribute_value_ids'] = [(6, 0, attribute_value_list)]
                new_template.product_variant_ids.write(product_vals)
                main_value_list[new_template.id] = attribute_value_list
            print ("Successfully", record)
            record += 1

        if rem_product_tmpl_desc:
            for rem_prod_tmpl_desc in rem_product_tmpl_desc:
                rem_prod_tmpl_desc.write({'description': ''})

        str_error = "\n".join(str(error_lst.index(x))+' '+str(x) for x in error_lst)
        head, tail = os.path.split(file_path)
        context = {}
        if len(bounced_cust) > 1:
            fecfile = self._write_bounced_file(bounced_cust, 'customer')
            url = self._get_bounced_url(fecfile, 'BOUNCED_CUTOMER.csv')
            context.update({'default_note': str_error, 'default_file_path': url, 'default_flag': True})
        _logger.info("Successfully completed import Product process.")
        if bounce_categs:
            fecfile = self._write_bounced_file(bounce_categs, 'web_categ')
            url = self._get_bounced_url(fecfile, 'Bounced_Web_Category.csv')
            context.update({'default_file_path2': url, 'default_flag': True})
        return {
                'name': _('Notification'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'output',
                'type': 'ir.actions.act_window',
                'target': 'new'
                }


class output(models.TransientModel):
    _name = 'output'
    _description = "Bounce file Output"

    file = fields.Binary(type='binary', string="Download File", readonly=True)
    file_path = fields.Char('Bounced Product File')
    file_path2 = fields.Char('Bounced Category File')
    flag = fields.Boolean()
    note = fields.Text()
