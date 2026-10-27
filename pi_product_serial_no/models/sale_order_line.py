from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    package = fields.Char(string='Package', compute='_compute_package_range', store=False)

    @api.depends('order_id.order_line', 'order_id.order_line.product_uom_qty')
    def _compute_package_range(self):
        for order in self.mapped('order_id'):
            current_serial = 0
            for line in order.order_line:
                if line.display_type:
                    if line in self:
                        line.package = ""
                    continue
                
                qty = line.product_uom_qty
                if qty > 0:
                    start = int(current_serial + 1)
                    end = int(current_serial + qty)
                    line.package = f"{start}-{end}"
                    current_serial = end
                else:
                    if line in self:
                        line.package = ""
                    # current_serial remains same
        
        # Ensure any lines in self that were not in the above loops (unlikely) get a value
        for line in self:
            if not line.package:
                line.package = ""
