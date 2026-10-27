# -*- coding: utf-8 -*-

from odoo import fields, models,api


def extract_part_after_second_slash(reference):
    parts = reference.split('/')
    if len(parts) > 2:
        return parts[-1]  # Return the part after the second /
    return False  # If there is no part after the second /

class InheritStockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_name = fields.Char(compute='_compute_lot_name', store=True, readonly=False)
    sl_no = fields.Integer(compute='_compute_lot_name', string="SL no.", store=True, readonly=False)



    @api.depends('move_id')
    def _compute_lot_name(self):
        for  rec in self:
            if rec.picking_id.picking_type_code == "incoming" and not rec.sl_no:
                if len(rec.move_id.move_line_ids) ==1:
                    sl= 1
                else:
                    max_sl = max(rec.move_id.move_line_ids.mapped('sl_no') or [0])
                    sl = max_sl + 1

                rec.sl_no = sl
                rec.lot_name = f"{rec.product_id.default_code}/{rec.picking_id.scheduled_date.strftime('%d%m%Y')}/{extract_part_after_second_slash(rec.picking_id.display_name)}"
                print(rec.lot_name)

    def action_open_lot(self):
        self.ensure_one()
        if self.lot_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.lot',
                'res_id': self.lot_id.id,
                'view_mode': 'form',
                'target': 'current',
            }