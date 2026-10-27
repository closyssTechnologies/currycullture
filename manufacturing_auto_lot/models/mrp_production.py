# -*- coding: utf-8 -*-

from odoo import fields, models,api
from odoo.exceptions import UserError

class InheritStockMoveLine(models.Model):
    _inherit = 'mrp.production'

    def _prepare_stock_lot_values_primacy(self):
        self.ensure_one()
        # res = super()._prepare_stock_lot_values()
        new_name =f"{self.product_id.default_code}/{self.date_finished.strftime('%d%m%Y')}/{self.name}"
        exist_lot = not new_name or self.env['stock.lot'].search([
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id),
            ('name', '=', new_name),
        ], limit=1)

        return {
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'name': new_name,
        }




    def button_mark_done(self):
        res = super().button_mark_done()
        if res:
            for rec in self:
                # if not rec.lot_producing_id:
                new_name = f"{rec.product_id.default_code}/{rec.date_finished.strftime('%d%m%Y')}/{rec.name}"
                # rec.lot_producing_id.name = self.env['stock.lot'].create(rec._prepare_stock_lot_values_primacy())
                rec.lot_producing_id.name = new_name

        return res








