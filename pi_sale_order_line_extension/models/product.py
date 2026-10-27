from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_studio_gross_weight = fields.Float(string="Gross Weight (Studio)")
