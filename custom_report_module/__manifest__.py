{
    'name': 'Custom Report Module',
    'version': '17.0.1.0',
    'author': "Primacy Infotech Pvt Ltd",
    'category': 'Purchases',
    'summary': 'Custom Purchase Report',
    'depends': ['purchase','account','sale', 'stock'],
    'data': [
        'reports/account_bill_report.xml',
        'reports/action_account_bill_report.xml',
        'reports/action_invoicing_report.xml',
        'reports/invoicing _report.xml',
        'reports/action_sale_report.xml',
        # 'reports/purchase_report_template.xml',
        'reports/sale_report.xml',

        'views/inherit_account_bill_report.xml',
        'views/inherit_invoicing_order_report.xml',
        # 'views/inherit_purchase_order_report.xml',
        'views/inherit_sale_order_report.xml',
        'views/account_move_line.xml',
        # 'reports/report_picking_operation.xml'


    ],
    'installable': True,
}
