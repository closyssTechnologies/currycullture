# -*- coding: utf-8 -*-

from odoo import fields, models, api


class InheritStockMoveLine(models.Model):
    _inherit = 'mrp.production'

    def _prepare_stock_lot_values_primacy(self):
        self.ensure_one()
        date_str = (self.date_finished or fields.Datetime.now()).strftime('%d%m%Y')
        prefix = self.product_id.default_code or self.product_id.name or 'LOT'
        new_name = f"{prefix}/{date_str}/{self.name}"

        return {
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'name': new_name,
        }

    def button_mark_done(self):
        res = super().button_mark_done()
        if res:
            for rec in self:
                date_str = (rec.date_finished or fields.Datetime.now()).strftime('%d%m%Y')
                prefix = rec.product_id.default_code or rec.product_id.name or 'LOT'
                new_name = f"{prefix}/{date_str}/{rec.name}"
                if hasattr(rec, 'lot_producing_ids') and rec.lot_producing_ids:
                    rec.lot_producing_ids.write({'name': new_name})
                elif hasattr(rec, 'lot_producing_id') and rec.lot_producing_id:
                    rec.lot_producing_id.name = new_name

        return res
