from odoo import fields,api,models

class BioResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    checkout_time_for_single_punch = fields.Float("Checkout Time for Single Punch",default=17.50)