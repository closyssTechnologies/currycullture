# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pre_carriage_by = fields.Char(string="Pre Carriage By")
    place_of_receipt = fields.Char(string="Place of Receipt By Pre Carrier")
    country_origin = fields.Char(string="Country of Origin of Goods", default="India")
    vessel_flight_no = fields.Char(string="Vessel/Flight No")
    port_loading = fields.Char(string="Port of Loading Name")
    port_discharge = fields.Char(string="Port of Discharge")
    final_destination = fields.Char(string="Final Destination")
    mark_no = fields.Char(string="Mark")
    container_no = fields.Char(string="Container No:")
    buyer_fda_no = fields.Char(string="Buyer FDA No")

    def _prepare_picking(self):
        res = super(SaleOrder, self)._prepare_picking()
        res.update({
            'pre_carriage_by': self.pre_carriage_by,
            'place_of_receipt': self.place_of_receipt,
            'country_origin': self.country_origin,
            'vessel_flight_no': self.vessel_flight_no,
            'port_loading': self.port_loading,
            'port_discharge': self.port_discharge,
            'final_destination': self.final_destination,
            'mark_no': self.mark_no,
            'container_no': self.container_no,
            'buyer_fda_no': self.buyer_fda_no,
        })
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pre_carriage_by = fields.Char(string="Pre Carriage By")
    place_of_receipt = fields.Char(string="Place of Receipt By Pre Carrier")
    country_origin = fields.Char(string="Country of Origin of Goods")
    vessel_flight_no = fields.Char(string="Vessel/Flight No")
    port_loading = fields.Char(string="Port of Loading Name")
    port_discharge = fields.Char(string="Port of Discharge")
    final_destination = fields.Char(string="Final Destination")
    mark_no = fields.Char(string="Mark")
    container_no = fields.Char(string="Container No:")
    buyer_fda_no = fields.Char(string="Buyer FDA No")
