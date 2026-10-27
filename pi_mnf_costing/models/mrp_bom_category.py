from odoo import models, fields

class MrpBomCategory(models.Model):
    _name = 'mrp.bom.category'
    _description = 'BOM Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
