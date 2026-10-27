from odoo import fields,models,api
from datetime import datetime


class ResCompany(models.Model):
    _inherit = 'res.company'


    def _get_financial_years(self):
        current_year = datetime.now().year
        years = []
        for i in range(-5, 10):  # Generate for previous 5 years and next 10 years
            start_year = (current_year + i) % 100  # Get last two digits
            end_year = (current_year + i + 1) % 100
            years.append((f'{start_year}-{end_year}', f'{start_year}-{end_year}'))
        return years

    financial_year = fields.Selection(selection=_get_financial_years, string="Financial Year")
    gate_pass_last_sl_no= fields.Integer(store=True,default =1)


    @api.onchange('financial_year')
    def onchange_financial_year(self):
        for rec in self:
            rec.gate_pass_last_sl_no = 1
