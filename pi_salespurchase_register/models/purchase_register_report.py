from odoo import models, fields, tools

class PurchaseRegisterReport(models.Model):
    _name = 'purchase.register.report'
    _description = 'Purchase Register Report'
    _auto = False
    _order = 'date_order desc'

    date_order = fields.Datetime(string='Date', readonly=True)
    purchase_order_no = fields.Char(string='Purchase Order No.', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    product_uom = fields.Many2one('uom.uom', string='UOM', readonly=True)
    price_unit = fields.Float(string='Unit Price', readonly=True)
    hsn_code = fields.Char(string='HSN Code', readonly=True)
    discount = fields.Float(string='Discount (%)', readonly=True)
    product_qty = fields.Float(string='Demand Quantity', readonly=True)
    qty_received = fields.Float(string='Received', readonly=True)
    # net_weight = fields.Float(string='Net Weight', readonly=True)
    remaining_qty = fields.Float(string='Remaining Qty', readonly=True)
    transfer_no = fields.Char(string='Transfer No.', readonly=True)
    is_billed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Billed', readonly=True)
    price_tax = fields.Float(string='Tax Amount', readonly=True)
    tax_percentage = fields.Char(string='Tax Percentage', readonly=True)
    price_total = fields.Float(string='Total Amount', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    pol.id AS id,
                    po.date_order AS date_order,
                    po.name AS purchase_order_no,
                    (
                        SELECT string_agg(DISTINCT sp.name, ', ')
                        FROM stock_picking sp
                        JOIN stock_move sm ON sm.picking_id = sp.id
                        JOIN stock_location src ON sm.location_id = src.id
                        JOIN stock_location dest ON sm.location_dest_id = dest.id
                        JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
                        WHERE 
                            sp.origin = po.name
                            AND spt.code = 'incoming'
                            AND sm.product_id = pol.product_id
                            AND pol.qty_received > 0
                            AND src.usage = 'supplier'
                            AND dest.usage IN ('internal')
                    ) AS transfer_no,
                    CASE 
                        WHEN pol.qty_invoiced > 0 THEN 'yes'
                        ELSE 'no'
                    END AS is_billed,
                    po.partner_id AS partner_id,
                    pol.product_id AS product_id,
                    pt.categ_id AS categ_id,
                    pol.product_uom AS product_uom,
                    pol.price_unit AS price_unit,
                    pt.l10n_in_hsn_code AS hsn_code,
                    pol.discount AS discount,
                    pol.product_qty AS product_qty,
                    pol.qty_received AS qty_received,
                    (pol.product_qty * pt.weight) AS net_weight,
                    (pol.product_qty - pol.qty_received) AS remaining_qty,
                    pol.price_tax AS price_tax,
                    (
                        SELECT string_agg(at.amount::text || '%%', ', ')
                        FROM account_tax_purchase_order_line_rel rel
                        JOIN account_tax at ON rel.account_tax_id = at.id
                        WHERE rel.purchase_order_line_id = pol.id
                    ) AS tax_percentage,
                    pol.price_total AS price_total
                FROM
                    purchase_order_line pol
                JOIN
                    purchase_order po ON pol.order_id = po.id
                JOIN
                    product_product pp ON pol.product_id = pp.id
                JOIN
                    product_template pt ON pp.product_tmpl_id = pt.id
                WHERE
                    po.state IN ('purchase', 'done')
            )
        """ % self._table)
