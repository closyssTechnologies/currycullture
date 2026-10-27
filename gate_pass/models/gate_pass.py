from odoo import models, fields


class GatePass(models.Model):
    _name = 'gate.pass'
    _description = 'Gate Pass'

    name = fields.Char('Gate Pass Number', default='New')
    visitor_name = fields.Char('Visitor Name')
    purpose = fields.Text('Purpose')
    entry_type = fields.Selection([
        ('inward', 'Inward'),
        ('outward', 'Outward')
    ], string='Entry Type', default='inward')