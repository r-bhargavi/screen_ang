{
    'name': 'Import Products By CSV File.',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 1,
    'summary': '',
    'description': """
        This module contains 2 script to Create/Update products, and Split Products\n
        1. Goto Menu Inventory > Manage Products > Import Products:
            it'll popup one wizard to select file and import it.\n
        2. Goto Menu Inventory > Manage Products > Split Products:
            it'll popup one wizard to select Product and Split It.
    """,
    'author': 'Kanak Infosystems LLP.',
    'website': 'http://www.kanakinfosystems.com',
    'depends': ['wws_product'],
    'data': [
        'wizard/import_product_view.xml',
        'wizard/split_product_view.xml',
     ],
    'installable': True,
}
