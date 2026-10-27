# -*- coding: utf-8 -*-
{
    'name': "PI BioSync",

    'summary': "PI BioSync Biometric integration with Fortuna",

    'description': """
PI BioSync Biometric integration with Fortuna HRMS
    """,

    'author': "Primacy Infotech Pvt Ltd",
    'website': "www.primacyinfotech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '17.0.3.2',

    # any module necessary for this one to work correctly
    'depends': ['base','hr',"hr_attendance"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ir_cron.xml',
        'views/resource_calender.xml',
        'wizard/device_assignment_wizard_view.xml',
        'wizard/bulk_biometric_group_wizard_view.xml',
        'views/biometric_config.xml',
        # 'views/res_users.xml',
        'views/hr_employee.xml',
        'views/res_config.xml',
        'views/biometric_attendance_log_view.xml',
        'views/hr_attendance.xml',



    ],
    'license': 'OPL-1',
}

