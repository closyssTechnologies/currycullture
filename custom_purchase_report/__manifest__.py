{
    'name': 'Custom Purchase Report',
    'version': '19.0.1.0.1',
    'author': "Primacy Infotech Pvt Ltd",
    'category': 'Purchases',
    'summary': 'Custom Purchase Report',
    'depends': ['purchase', 'account'],
    'data': [
        'reports/purchase_report_template.xml',
        'views/inherit_purchase_order_report.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
