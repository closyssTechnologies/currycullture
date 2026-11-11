{
    'name': 'PI Sale Order Line Extension',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Add Total Weight and Total Value fields to Sale Order Lines',
    'description': """
        This module extends the sale order line to include:
        - Total Weight field (computed based on product weight and quantity)
        - Total Value field (computed based on unit price and quantity)
    """,
    'author': 'Primacy Infotech Pvt Ltd',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
