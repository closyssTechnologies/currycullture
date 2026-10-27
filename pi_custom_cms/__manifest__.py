{
    'name': 'Credit Management Sheet',
    'version': '17.0.1.2',
    'summary': 'Manage daily vendor payments and generate credit management sheets',
    'description': """
Credit Management Sheet
=======================
This module adds a menu under Accounting for managing daily vendor credit payments.
It generates a credit management sheet (CMS) for bank submission.
    """,
    'author': 'Primacy Infotech Pvt Ltd',
    'website': 'https://primacyinfotech.com/',
    'depends': ['account','base'],  # links this to the Accounting app
    'data': [
        'security/ir.model.access.csv',
        'views/credit_management_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
