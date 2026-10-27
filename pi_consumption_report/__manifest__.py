{
    'name': 'PI Consumption Report',
    'version': '17.0',
    'category': 'Inventory/Reporting',
    'summary': 'Daily Material Consumption Report',
    'author': 'Primacy Infotech Pvt Ltd',
    'depends': ['stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/consumption_report_view.xml',
        'wizard/consumption_report_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
