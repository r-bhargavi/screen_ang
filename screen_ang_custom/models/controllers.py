# -*- coding: utf-8 -*-
try:
    import json
except ImportError:
    import simplejson as json


import odoo.addons.web.http as openerpweb
from odoo.addons.web.controllers.main import ExcelExport


class ExcelExportView(ExcelExport):
    _cp_path = '/web/export/xls_view'

    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)

    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])
        filename = data.get('filename', False)

        return req.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                    % (self.filename(filename) or self.filename(model))),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: