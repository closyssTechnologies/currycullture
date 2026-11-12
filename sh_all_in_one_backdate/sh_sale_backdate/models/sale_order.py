# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

from datetime import date
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    remarks = fields.Text(string="Remarks")
    is_remarks = fields.Boolean(
        related="company_id.remark_for_sale_order", string="Is Remarks")
    is_remarks_mandatory = fields.Boolean(
        related="company_id.remark_mandatory_for_sale_order", string="Is remarks mandatory")
    is_boolean = fields.Boolean()

    @api.onchange('date_order')
    def onchange_date_order(self):
        if self.date_order:
            if str(self.date_order.date()) < str(date.today()):
                self.is_boolean = True
            else:
                self.is_boolean = False

    def _prepare_confirmation_values(self):
        if self.company_id.backdate_for_sale_order:
            return {
                'state': 'sale',
            }
        else:
            return {
                'state': 'sale',
                'date_order': fields.Datetime.now()
            }

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a sales order.
        """
        invoice_vals = super()._prepare_invoice()
        if self.company_id.backdate_for_invoice and self.date_order:
            invoice_vals['invoice_date'] = fields.Date.to_date(self.date_order)
        if self.remarks:
            invoice_vals['remarks_for_sale'] = self.remarks
        return invoice_vals
