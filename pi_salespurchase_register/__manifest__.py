{
    'name': 'Sales & Purchase Register Report',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Add Sales and Purchase Register report in Reporting',
    'description': """
        Add Sales and Purchase Register Report in Odoo.
    """,
    'author': 'Primacy Infotech Pvt Ltd',
    'depends': ['purchase', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_register_view.xml',
        'views/sale_register_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
