{
    'name': 'Custom_Product_Label_Report',
    'version': '19.0.1.0.0',
    'author': "Primacy Infotech Pvt Ltd",
    'category': 'Purchases',
    'summary': 'Custom Purchase Report',
    'depends': ['purchase', 'stock', 'account'],
    'data': [
        'reports/stock_picking_report.xml',
        'views/inherit_view_picking_form_inherit.xml'
    ],
    'installable': True,
    'license': 'LGPL-3',
}
