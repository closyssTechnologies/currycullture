# -*- coding: utf-8 -*-
# Part of Softhealer Technologies


from odoo import fields, models, api
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    remarks_for_sale = fields.Text(
        string="Remarks for Sale", related="sale_id.remarks")
    is_remarks_for_sale = fields.Boolean(
        related="company_id.remark_for_sale_order", string="Is Remarks for Sale")

    # @api.depends('move_ids.state', 'move_ids.date', 'move_type')
    # def _compute_scheduled_date(self):
    #     super()._compute_scheduled_date()
    #     for picking in self:
    #         if picking.company_id.sh_so_backdate_for_stock_move and picking.sale_id:
    #             picking.scheduled_date = picking.sale_id.date_order

    def write(self, vals):
        for rec in self:
            if rec.sale_id and 'date_done' in vals and rec.company_id.sh_so_backdate_for_stock_move:
                vals['date_done'] = rec.sale_id.date_order

            return super().write(vals)

    def _set_scheduled_date(self):
        for picking in self:
            # if picking.state in ('done', 'cancel'):
            #     raise UserError(_("You cannot change the Scheduled Date on a done or cancelled transfer."))
            picking.move_lines.write({'date': picking.scheduled_date})
