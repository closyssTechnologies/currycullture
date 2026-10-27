{
    'name': 'Packing List for Export PDF',
    'version': '1.0',
    'summary': 'Generates a hardcoded Packing List for Export PDF from Delivery',
    'category': 'Inventory/Delivery',
    'author': 'Primacy Infotech Pvt. Ltd.',
    'depends': ['stock', 'sale_stock'],
    'data': [
        'views/stock_picking_views.xml',
        'views/product_template_views.xml',
        'reports/report_actions.xml',
        'reports/report_consignment_details.xml',
        'reports/report_packing_list.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
