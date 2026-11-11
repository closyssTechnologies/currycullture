from odoo import models, fields


class HrVersion(models.Model):
    _inherit = 'hr.version'

    per_day_wage = fields.Float(string="CTC(Month)")
