from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    per_day_wage = fields.Float(string="CTC(Month)")
