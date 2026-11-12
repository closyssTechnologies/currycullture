# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

from datetime import date
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    remarks = fields.Text(string="Remarks")
    is_remarks = fields.Boolean(
        related="company_id.remark_for_purchase_order", string="Is Remarks")
    is_remarks_mandatory = fields.Boolean(
        related="company_id.remark_mandatory_for_purchase_order", string="Is remarks mandatory")
    is_boolean = fields.Boolean()

    @api.onchange('date_order')
    def onchange_date_order(self):
        if self.date_order:
            if str(self.date_order.date()) < str(date.today()):
                self.is_boolean = True
            else:
                self.is_boolean = False

    def button_confirm(self, force=False):
        res = super().button_confirm()
        if self.company_id.backdate_for_purchase_order:
            self.write({
                'date_approve': self.date_order
            })
        return res

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        invoice_vals = super()._prepare_invoice()
        if self.company_id.backdate_for_bill:
            approve_date = self.date_approve or self.date_order
            if approve_date:
                invoice_vals['invoice_date'] = fields.Date.to_date(approve_date)
        if self.remarks:
            invoice_vals['remarks_for_purchase'] = self.remarks
        return invoice_vals


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super()._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom)
        if self.order_id.remarks:
            res['remarks_for_purchase'] = self.order_id.remarks
        return res
