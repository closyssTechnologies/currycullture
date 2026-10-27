from odoo import models, fields

class InheritStockMove(models.Model):
    _inherit = 'stock.move'

    mfg_date = fields.Date(string='Manufacturing Date')
    best_before = fields.Date(string='Best Before')
    net_wt = fields.Integer(string='Net Weight')