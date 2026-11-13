# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals and vals['state'] == 'done' and self.mo_id:
            stock_moves = self.env['stock.move'].search(
                ['|', ('unbuild_id', '=', self.id), ('consume_unbuild_id', '=', self.id)])
            product_moves = self.env['stock.move.line'].search(
                [('move_id', 'in', stock_moves.ids)])

            # In Odoo 19, stock.move links directly to account_move_id
            account_moves = stock_moves.account_move_id if hasattr(stock_moves, 'account_move_id') else self.env['account.move']

            for account_move in account_moves:
                account_move.button_draft()
                account_move.name = '/'
                account_move.date = self.mo_id.date_start
                account_move.action_post()

            for move in stock_moves:
                move.date = self.mo_id.date_start
                move.remarks_for_mrp = self.mo_id.remarks if self.mo_id.remarks else ''

            for move in product_moves:
                move.date = self.mo_id.date_start

        return res
