from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    packing_size = fields.Float(string="Packing Size")
