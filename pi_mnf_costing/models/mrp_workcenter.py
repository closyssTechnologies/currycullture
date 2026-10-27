from odoo import models, fields

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    employee_ids = fields.Many2many('hr.employee', string='Assigned Employees')
