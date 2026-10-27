{
    'name': 'Gate Pass',
    'version': '17.0.1.1.2',
    'summary': 'Manage Inward and Outward Gate Operations',
    'description': """
Gate Pass Management Module
===========================
This module allows you to manage inward and outward gate operations.
Key Features:
- Track Inward and Outward movements.
- Link with Purchase Orders.
- Capture Weight, Vehicle, and Driver details.
- Multi-stage approval process (Entry -> Hold -> Exit).
""",
    'category': 'Other',
    'author': 'Primacy Infotech Pvt. Ltd.',
    'depends': ['base', 'web', 'purchase', 'stock', 'sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'reports/inward_receipt_report.xml',
        'reports/outward_gate_report.xml',
        'views/gate_pass_views.xml',
        'views/res_users_views.xml',
        'views/inward_operation_views.xml',
        'views/outward_operation_views.xml',
        'views/stock_picking_views.xml',
        'views/sale_purchase_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'gate_pass/static/src/js/gate_entry_dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
}
