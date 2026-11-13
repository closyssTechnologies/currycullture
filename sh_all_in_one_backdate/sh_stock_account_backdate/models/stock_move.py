# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _create_account_move(self):
        res = super()._create_account_move()
        for move in self:
            if move.account_move_id and move.date:
                move.account_move_id.write({'date': move.date.date() if hasattr(move.date, 'date') else move.date})
        return res
