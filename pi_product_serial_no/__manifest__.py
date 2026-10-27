{
    'name': 'Product Serial Number Range',
    'version': '1.0',
    'summary': 'Add cumulative serial number range to sale order lines',
    'category': 'Sales',
    'author': 'Primacy Infotech Pvt. Ltd.',
    'website': 'https://www.primacyinfotech.com',
    'depends': ['sale', 'purchase'],
    'data': [
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
