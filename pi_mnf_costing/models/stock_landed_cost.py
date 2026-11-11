from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    # Override the field to remove group restrictions
    # This allows all users to access manufacturing orders in landed costs
    mrp_production_ids = fields.Many2many(
        'mrp.production',
        string='Manufacturing order',
        copy=False,
        prefetch=False   # ⭐ THIS IS THE ACTUAL FIX
    )

    def check_field_access_rights(self, operation: str, field_names: list[str] | None = None, *args, **kwargs) -> list[str]:
        fnames = field_names if field_names is not None else kwargs.get('fields')
        res = super().check_field_access_rights(operation, field_names=fnames, *args, **kwargs)
        if fnames and 'mrp_production_ids' in fnames and isinstance(res, list) and 'mrp_production_ids' not in res:
            res.append('mrp_production_ids')
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for res, vals in zip(records, vals_list):
            if 'picking_ids' in vals and res.picking_ids:
                for picking in res.picking_ids:
                    mo = self.env['mrp.production'].search([('picking_ids', 'in', picking.id)], limit=1)
                    if mo and mo.landed_cost:
                        product = self._get_or_create_landed_cost_product('Manual MRP')
                        account_id = res._get_default_account_id() if hasattr(res, '_get_default_account_id') else False
                        res.cost_lines = [(0, 0, {
                            'name': 'Manual MRP Landed Cost',
                            'product_id': product.id,
                            'account_id': account_id,
                            'price_unit': mo.landed_cost,
                            'split_method': 'equal',
                        })]
        return records

    def _landed_cost_cron(self):
        today = fields.Date.today()
        start = fields.Datetime.to_datetime(f"{today} 00:00:00")
        end = fields.Datetime.to_datetime(f"{today} 23:59:59")
        
        mo_records = self.env['mrp.production'].search([
            ('date_finished', '>=', start),
            ('date_finished', '<=', end),
            ('state', '=', 'done')
        ])
        
        if not mo_records:
            return
        

        # electricity_cost = sum(mo.electricity_cost for mo in mo_records if mo.electricity_cost)
        # gas_cost = sum(mo.gas_cost for mo in mo_records if mo.gas_cost)
        # water_cost = sum(mo.water_cost for mo in mo_records if mo.water_cost)
        # labor_cost = sum(mo.labor_cost for mo in mo_records if mo.labor_cost)

        # total_cost = electricity_cost + gas_cost + water_cost + labor_cost;
        
        # if total_cost == 0:
        #     return

        # Aggregate individual cost types
        cost_data = {
            'Electricity': sum(mo.electricity_cost for mo in mo_records if mo.electricity_cost),
            'Gas': sum(mo.gas_cost for mo in mo_records if mo.gas_cost),
            'Water': sum(mo.water_cost for mo in mo_records if mo.water_cost),
            'Labour': sum(mo.labor_cost for mo in mo_records if mo.labor_cost),
        }

        # Filter out zero-costs
        cost_data = {name: value for name, value in cost_data.items() if value > 0}
        if not cost_data:
            return
        print(cost_data)
        # product = self._get_or_create_landed_cost_product()

        journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        if not journal:
            journal = self.env['account.journal'].create({
                'name': 'General Journal',
                'code': 'GEN',
                'type': 'general',
                'company_id': self.env.company.id,
            })

        account = self.env['account.account'].search([('name', '=', 'Closing stock (P&L) - Gujrat')], limit=1)
        if not account:
            account = self.env['account.account'].create({
                'name': 'Closing stock (P&L) - Gujrat',
                'code': '201201',
                'account_type': 'asset_current',  # You can change depending on your needs
                'company_id': self.env.company.id,
            })

        if not journal or not account:
            raise ValueError("General Journal or Landed Costs account not configured properly.")

        cost_lines = []
        for cost_name, cost_value in cost_data.items():
            product = self._get_or_create_landed_cost_product(cost_name)
            cost_lines.append((0, 0, {
                'name': f'{cost_name} Cost',
                'product_id': product.id,
                'account_id': account.id,
                'price_unit': cost_value,
                'split_method': 'equal',
            }))

        # landed_cost = self.create({
        #     'target_model': 'manufacturing',
        #     'mrp_production_ids': [(6, 0, mo_records.ids)],
        #     'account_journal_id': journal.id,
        #     'cost_lines': [(0, 0, {
        #         'name': 'Auto MRP Landed Cost',
        #         'product_id': product.id,
        #         'account_id': account.id,
        #         'price_unit': total_cost,
        #         'split_method': 'equal',
        #     })],
        # })

        landed_cost = self.create({
            'target_model': 'manufacturing',
            'mrp_production_ids': [(6, 0, mo_records.ids)],
            'account_journal_id': journal.id,
            'cost_lines': cost_lines,
        })

        landed_cost.compute_landed_cost()
        landed_cost.button_validate()

    def _get_or_create_landed_cost_product(self, name):
        product = self.env['product.product'].search([
            ('name', '=', f'{name} Cost Product'),
            ('landed_cost_ok', '=', True)
        ], limit=1)
        if not product:
            tmpl = self.env['product.template'].create({
                'name': f'{name} Cost Product',
                'type': 'service',
                'purchase_ok': True,
                'sale_ok': False,
                'landed_cost_ok': True,
                'purchase_method': 'purchase',
            })
            product = tmpl.product_variant_id
        return product

    # def _get_or_create_landed_cost_product(self):
    #     product = self.env['product.product'].search([
    #         ('name', '=', 'Auto Landed Cost Product'),
    #         ('landed_cost_ok', '=', True)
    #     ], limit=1)
    #     if not product:
    #         tmpl = self.env['product.template'].create({
    #             'name': 'Auto Landed Cost Product',
    #             'type': 'service',
    #             'purchase_ok': True,
    #             'sale_ok': False,
    #             'landed_cost_ok': True,
    #             'purchase_method': 'purchase',
    #         })
    #         product = tmpl.product_variant_id
    #     return product
