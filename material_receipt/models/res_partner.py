from odoo import fields,models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    bank_account_name = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Bank Name',
        )
    bank_account_no = fields.Char(related='bank_account_name.acc_number', string='Bank Account No')

