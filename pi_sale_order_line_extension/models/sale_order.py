from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_volume = fields.Float(
        string="Volume",
        related='product_id.product_tmpl_id.volume',
        readonly=True,
        store=True
    )
    product_weight = fields.Float(
        string="Weight",
        related='product_id.product_tmpl_id.weight',
        readonly=True,
        store=True
    )

    total_volume = fields.Float(
        string="Volume kg",
        compute='_compute_total_volume',
        store=True,
        readonly=True
    )

    total_weight = fields.Float(
        string="Weight m³",
        compute='_compute_total_weight',
        store=True,
        readonly=True
    )

    net_weight = fields.Float(
        string="Net Weight",
        compute='_compute_weights',
        store=True,
        readonly=True
    )

    gross_weight = fields.Float(
        string="Gross Weight",
        compute='_compute_weights',
        store=True,
        readonly=True
    )

    @api.depends('product_volume', 'product_uom_qty')
    def _compute_total_volume(self):
        for line in self:
            line.total_volume = line.product_volume * line.product_uom_qty

    @api.depends('product_weight', 'product_uom_qty')
    def _compute_total_weight(self):
        for line in self:
            line.total_weight = line.product_weight * line.product_uom_qty
    
    @api.depends('product_id.weight', 'product_id.x_studio_gross_weight', 'product_uom_qty')
    def _compute_weights(self):
        for line in self:
            line.net_weight = (line.product_id.weight or 0.0) * line.product_uom_qty
            line.gross_weight = ((line.product_id.x_studio_gross_weight or 0.0) * line.product_uom_qty) + line.net_weight