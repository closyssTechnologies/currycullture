# -*- coding: utf-8 -*-
{
    'name': "Material Receipt Report",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

   'author': "Primacy Infotech Pvt Ltd",
    'website': "https://primacyinfotech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','gatepass_slip'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partners.xml',
        'report/material_receipt.xml'
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'license': 'LGPL-3',
}

