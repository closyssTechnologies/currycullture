{
    'name': 'PI Certificate of Analysis',
    'version': '1.0',
    'summary': 'Certificate of Analysis Module',
    'description': 'Creates a menu under Quality Control to manage Certificate of Analysis',
    'author': 'Primacy Infotech Pvt Ltd',
    'depends': ['base', 'mail', 'quality', 'quality_control', 'product', 'hr', 'sign'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'report/certificate_analysis_report.xml',
        'views/certificate_analysis_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
