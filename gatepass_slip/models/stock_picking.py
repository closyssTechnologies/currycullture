# -*- coding: utf-8 -*-
###############################################################################
#    Cybrosys Technologies Pvt. Ltd.
from email.policy import default

#    Copyright(C) 2024-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Jumana Haseen (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Lesser General Public License(LGPLv3) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields, models,api


# class GatePassResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#
#
#
#     gate_pass_last_sl_no= fields.Integer(store=True,config_parameter='gatepass_slip.gate_pass_last_sl_no' ,default =1)
#

class StockPicking(models.Model):
    """Inherit model 'stock.picking' and add required fields """
    _inherit = 'stock.picking'


    def _get_pass_no(self):
        # sl_no=self.env['ir.config_parameter'].sudo().get_param('gatepass_slip.gate_pass_last_sl_no')
        sl_no=self.env.company.gate_pass_last_sl_no
        gate_pass = f'PL/CCL/GET-{self.env.company.financial_year}-{sl_no:06}'
        self.env.company.gate_pass_last_sl_no = sl_no+1
        # self.env['ir.config_parameter'].sudo().set_param('gatepass_slip.gate_pass_last_sl_no',sl_no+1)
        return gate_pass

    def _default_getpass(self):
        return f'PL/CCL/GET-{self.env.company.financial_year}-'


    is_enable_order_line = fields.Boolean(string='Include Product Details',
                                          default=True,
                                          help="If you want to print the "
                                               "product details in your report"
                                               " enable this field.")
    vehicle_no = fields.Char(string='Vehicle Number',
                             help="Enter the vehicle number.")
    vehicle_driver_name = fields.Char(string='Driver Name',
                                      help="Enter the driver's name.")
    driver_contact_number = fields.Char(string='Contact No',
                                        help="Enter the driver's contact"
                                             " number.")
    corresponding_company = fields.Char(string='Company',
                                        help="Enter the corresponding company.")
    financial_year = fields.Selection(string='Financial Year',related='company_id.financial_year')
    gate_pass_no = fields.Char(string='Gate Pass Number',

                                          help="Gate Pass no .", default=_default_getpass,copy=False)
    gate_received_date = fields.Datetime(string='Receive Date & Time',copy=False)
    # gate_pass_sl_no = fields.Integer(compute='_compute_lot_name', string="SL no.", store=True)
    gate_pass_no_readonly = fields.Boolean(compute='_compute_gate_pass_no_readonly')

    @api.onchange('state')
    def _compute_gate_pass_no_readonly(self):
        for rec in self:
            rec.gate_pass_no_readonly = (rec.state == 'done' and not self.env.user.has_group('stock.group_stock_manager'))

    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super().create(vals_list)
    #     for vals in vals_list:
    #         vals.update({'need_sync_m': False})
    #
    #     print(records)

    def write(self, vals):
        if 'date_done' in vals and self.picking_type_code not in ['internal']:
            # company = self.company_id.sudo()
            # sl_no=company.gate_pass_last_sl_no
            #
            # gate_pass = f'PL/CCL/GET-{company.financial_year}'
            # company.gate_pass_last_sl_no = sl_no+1
            # vals['gate_pass_no'] = gate_pass
            vals['gate_received_date'] = vals['date_done']
        res = super(StockPicking, self).write(vals)


        return res

    # @api.depends('state')
    # def _get_pass_no(self):
    #     # sl_no=self.env['ir.config_parameter'].sudo().get_param('gatepass_slip.gate_pass_last_sl_no')
    #     sl_no=self.env.company.gate_pass_last_sl_no
    #     gate_pass = f'PL/CCL/GET-{self.env.company.financial_year}-{sl_no:06}'
    #     self.env.company.gate_pass_last_sl_no = sl_no+1
    #     # self.env['ir.config_parameter'].sudo().set_param('gatepass_slip.gate_pass_last_sl_no',sl_no+1)
    #     return gate_pass
