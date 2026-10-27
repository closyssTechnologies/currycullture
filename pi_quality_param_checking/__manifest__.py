# -*- coding: utf-8 -*-
{
    'name': "PI Quality Check",

    'summary': "Added new feature to track extra parameters for QC",

    'description': """
Added new feature to track extra parameters for QC
    """,

    'author': "Primacy Infotech Pvt Ltd",
    'website': "https://primacyinfotech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Quality',
    'version': '17.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['quality','quality_control'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/quality_check.xml',
        'wizards/quality_check_wiz_view.xml',
    ],
    'license': 'LGPL-3',
}

