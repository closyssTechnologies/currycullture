# -*- coding: utf-8 -*-
{
    'name': "Manufacturing Auto Lot/Serial No Set",

    'summary': "Manufacturing Auto Lot/Serial No Set When Produce",

    'description': """
        Manufacturing Auto Lot/Serial No Set When Produce
    """,

    'author': "Primacy Infotech Pvt Ltd",
    'website': "https://www.primacyinfotech.com",
    'maintainer': 'developer@primacyinfotech.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '17.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        'views/mrp_production.xml'
    ],
    'license': 'LGPL-3',
}

