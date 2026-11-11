# -*- coding: utf-8 -*-
{
    'name': "PI Quality Check",
    'summary': "Added new feature to track extra parameters for QC",
    'description': """
Added new feature to track extra parameters for QC
    """,
    'author': "Primacy Infotech Pvt Ltd",
    'website': "https://primacyinfotech.com",
    'category': 'Manufacturing/Quality',
    'version': '19.0.1.0.0',
    'depends': ['quality', 'quality_control'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/quality_check.xml',
        'wizards/quality_check_wiz_view.xml',
    ],
    'license': 'LGPL-3',
}
