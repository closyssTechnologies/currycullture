{
    'name': 'Custom_Product_Label_Report',
    'version': '17.0.0.3',
    'author': "Primacy Infotech Pvt Ltd",
    'category': 'Purchases',
    'summary': 'Custom Purchase Report',
    'depends': ['purchase','account'],
    'data': [
        'reports/stock_picking_report.xml',
        'views/inherit_view_picking_form_inherit.xml'
    ],
    'installable': True,
}
