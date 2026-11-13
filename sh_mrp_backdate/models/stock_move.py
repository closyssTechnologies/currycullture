# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    remarks_for_mrp = fields.Text(string="Remarks for MRP")
    is_remarks_for_mrp = fields.Boolean(
        related="company_id.remark_for_mrp_production", string="Is Remarks for MRP")

    def write(self, vals):
        for rec in self:
            if rec.company_id.enable_backdate_for_mrp:
                if rec.raw_material_production_id:
                    vals['date'] = rec.raw_material_production_id.date_start
                    vals['remarks_for_mrp'] = rec.raw_material_production_id.remarks

                if rec.production_id:
                    vals['date'] = rec.production_id.date_start
                    vals['remarks_for_mrp'] = rec.production_id.remarks

                if rec.created_production_id:
                    vals['date'] = rec.created_production_id.date_start
                    vals['remarks_for_mrp'] = rec.created_production_id.remarks

            return super(StockMove, self).write(vals)
