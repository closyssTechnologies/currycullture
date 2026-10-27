# -*- coding: utf-8 -*-
{
    'name': "Utility Meters/Counters base",

    'summary': """
        HMS Meters base module - tracking values of utility or any other type of meters/counters.""",

    'description': """
        HMS Meters/Counters base module is used for basic tracking values of utility or any other type of meters/counters
        like electricity, gas, heat, hot water, cold water, fuel, or any other type of meters or counters
        which you use in your business operations. It might be useful for real estate operations, like rental 
        or real estate management business, hotel or apartment hotel management, manufacturing business etc.
    """,

    'author': "Primacy Infotech Pvt Ltd",
    'website': "https://www.primacyinfotech.com",
    'support': "odoo@primacyinfotech.com",
    'category': 'Extra Tools',
    'version': '17.0.1.1',
    'images': ['static/description/meter_data.png'],
    'depends': ['base', 'mail'],

    'data': [
        # security
        'security/hms_meter_security.xml',
        'security/ir.model.access.csv',

        # Model views
        'views/hms_meter.xml',
        'views/hms_meter_type.xml',
        'views/hms_meter_data.xml',

        # data - cron, menus, records        
        'data/menus.xml',

    ],
    'qweb': [],
    'demo': [],
    'auto_install': False,
    'installable': True,
    'application': True,
    "price": 49,
    "currency": "EUR"
}

