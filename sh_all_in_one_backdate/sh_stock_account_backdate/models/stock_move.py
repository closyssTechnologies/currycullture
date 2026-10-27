# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        move_ids = self._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id, svl_id, description)

        if self.env.context.get('force_period_date'):
            self.date = self.env.context.get('force_period_date')

        return {
            'journal_id': journal_id,
            'line_ids': move_ids,
            'partner_id': valuation_partner_id,
            'date': self.date,
            'ref': description,
            'stock_move_id': self.id,
            'stock_valuation_layer_ids': [(6, None, [svl_id])],
            'move_type': 'entry',
        }
