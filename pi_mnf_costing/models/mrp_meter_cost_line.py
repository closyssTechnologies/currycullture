from odoo import models, fields

class MrpMeterCostLine(models.Model):
    _name = 'mrp.meter.cost.line'
    _description = 'Meter Cost Allocated to MO'

    production_id = fields.Many2one('mrp.production', required=True)
    meter_type_id = fields.Many2one('hms.meter.type', required=True)
    allocated_cost = fields.Float(string="Allocated Cost")
