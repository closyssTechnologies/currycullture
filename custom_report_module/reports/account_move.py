from odoo import api, fields, models


class InheritAccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super(InheritAccountMove, self).get_view(view_id, view_type, **options)
        return res


class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_packaging_quantity = fields.Float(string='Packaging Quantity')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update(
            {
                'product_packaging_quantity': self.product_packaging_qty,
            }
        )
        return res
