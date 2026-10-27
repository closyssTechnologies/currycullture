from odoo import models, fields, api, tools

class PiConsumptionReport(models.Model):
    _name = 'pi.consumption.report'
    _description = 'Daily Consumption Report'
    _auto = False
    _order = 'date desc'

    date = fields.Date('Date', readonly=True)
    source = fields.Char('Source', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    category_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    uom_id = fields.Many2one('uom.uom', 'UOM', readonly=True)
    quantity = fields.Float('Consumed Qty', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    sml.id AS id,
                    sml.date::date AS date,
                    sml.reference AS source,
                    sml.product_id AS product_id,
                    pt.categ_id AS category_id,
                    sml.product_uom_id AS uom_id,
                    sml.quantity AS quantity
                FROM
                    stock_move_line sml
                    JOIN product_product pp ON sml.product_id = pp.id
                    JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    JOIN stock_location sl_src ON sml.location_id = sl_src.id
                    JOIN stock_location sl_dest ON sml.location_dest_id = sl_dest.id
                WHERE
                    sml.state = 'done'
                    AND sl_src.usage = 'internal'
                    AND sl_dest.usage != 'internal'
                    AND sml.date::date <= CURRENT_DATE
            )
        """ % self._table)
