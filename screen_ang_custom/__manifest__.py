# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing Customization Administration',
    'version': '11.0',
    'category': 'Customized integration',
    'author': 'TechnoSavvy Solutions Pvt Ltd.',
    'website': 'http://www.technosavvy.net/',
    'description': """
Legal Information Administration.
===================================================

Used for Creating Legal Information

    """,
    'depends': [
        'base',
        'crm',
        'sale',
        'purchase',
        'stock',
        'mrp',
    ],
    'js': ['static/src/js/*.js'],
    'qweb': ['static/src/xml/export_inward_register.xml',
             ],
    'data': [
        'masters/arbitrator_master_view.xml',
        'routine_entries/views/case_sheet_sequence.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
