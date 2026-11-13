# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models
from datetime import date


class MrpProductionn(models.Model):
    _inherit = 'mrp.production'

    remarks = fields.Text(string="Remarks")
    is_remarks = fields.Boolean(
        related="company_id.remark_for_mrp_production", string="Is Remarks")
    is_remarks_mandatory = fields.Boolean(
        related="company_id.remark_mandatory_for_mrp_production", string="Is remarks mandatory")
    is_boolean = fields.Boolean()

    def write(self, vals):
        res = super().write(vals)
        for mrp_production in self:
            stock_moves = self.env['stock.move'].search(['|', '|', '|', ('production_id', '=', mrp_production.id), (
                'created_production_id', '=', mrp_production.id), ('raw_material_production_id', '=', mrp_production.id), ('origin', '=', mrp_production.name)])
            product_moves = self.env['stock.move.line'].search(
                [('move_id', 'in', stock_moves.ids)])

            # In Odoo 19, stock.move links directly to account_move_id (stock.valuation.layer is removed)
            account_moves = stock_moves.account_move_id if hasattr(stock_moves, 'account_move_id') else self.env['account.move']

            for account_move in account_moves:
                account_move.button_draft()
                account_move.name = '/'
                account_move.date = mrp_production.date_start
                account_move.action_post()

            for move in stock_moves:
                move.date = mrp_production.date_start
                move.remarks_for_mrp = mrp_production.remarks if mrp_production.remarks else ''

            for move in product_moves:
                move.date = mrp_production.date_start

        return res

    @api.onchange('date_start')
    def onchange_date_start(self):
        if self.date_start and str(self.date_start.date()) < str(date.today()):
            self.is_boolean = True
        else:
            self.is_boolean = False
