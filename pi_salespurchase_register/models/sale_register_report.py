from odoo import models, fields, tools

class SaleRegisterReport(models.Model):
    _name = 'sale.register.report'
    _description = 'Sales Register Report'
    _auto = False
    _order = 'date_order desc'

    date_order = fields.Datetime(string='Order Date', readonly=True)
    order_no = fields.Char(string='Order Number', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    product_uom = fields.Many2one('uom.uom', string='UOM', readonly=True)
    product_qty = fields.Float(string='Order Quantity', readonly=True)
    qty_delivered = fields.Float(string='Delivered Quantity', readonly=True)
    net_weight = fields.Float(string='Net Weight', readonly=True)
    price_unit = fields.Float(string='Unit Price', readonly=True)
    hsn_code = fields.Char(string='HSN Code', readonly=True)
    discount = fields.Float(string='Discount (%)', readonly=True)
    price_tax = fields.Float(string='Tax Amount', readonly=True)
    tax_percentage = fields.Char(string='Tax Label', readonly=True)
    price_total = fields.Float(string='Total Amount', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    sol.id AS id,
                    so.date_order AS date_order,
                    so.name AS order_no,
                    so.partner_id AS partner_id,
                    sol.product_id AS product_id,
                    pt.categ_id AS categ_id,
                    sol.product_uom AS product_uom,
                    sol.product_uom_qty AS product_qty,
                    sol.qty_delivered AS qty_delivered,
                    (sol.product_uom_qty * pt.weight) AS net_weight,
                    sol.price_unit AS price_unit,
                    pt.l10n_in_hsn_code AS hsn_code,
                    sol.discount AS discount,
                    sol.price_tax AS price_tax,
                    (
                        SELECT string_agg(at.name->>'en_US', ', ')
                        FROM account_tax_sale_order_line_rel rel
                        JOIN account_tax at ON rel.account_tax_id = at.id
                        WHERE rel.sale_order_line_id = sol.id
                    ) AS tax_percentage,
                    sol.price_total AS price_total
                FROM
                    sale_order_line sol
                JOIN
                    sale_order so ON sol.order_id = so.id
                JOIN
                    product_product pp ON sol.product_id = pp.id
                JOIN
                    product_template pt ON pp.product_tmpl_id = pt.id
                WHERE
                    so.state IN ('sale', 'done')
            )
        """ % self._table)
