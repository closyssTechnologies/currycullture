# -*- coding: utf-8 -*-
{
    'name': "Purchase Auto Lot/Serial No Set",

    'summary': "Purchase Auto Lot/Serial No Set When Receive",

    'description': """
        Purchase Auto Lot/Serial No Set When Receive
    """,

    'author': "Primacy Infotech Pvt Ltd",
    'website': "https://www.primacyinfotech.com",
    'maintainer': 'jahin.chisty@gmail.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '17.0.0.4',

    # any module necessary for this one to work correctly
    'depends': ['purchase','stock'],

    # always loaded
    'data': [
        'views/stock_move_views.xml',
    ],
    'license': 'OPL-1',
}

