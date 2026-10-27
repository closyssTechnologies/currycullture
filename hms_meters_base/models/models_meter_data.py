# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
_logger = logging.getLogger(__name__)


class HmsMeterData(models.Model):
    _name = 'hms.meter.data'
    _description = 'HMS Meter Data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    _order = 'data_datetime desc'

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, "%s [%s - %s]" % (r.meter_id.name, r.data_datetime, r.data)))

        return result

    meter_id = fields.Many2one(comodel_name='hms.meter', string='Meter', required=True)
    meter_type_id = fields.Many2one(related='meter_id.meter_type_id', string='Meter type', store=True)

    data_datetime = fields.Datetime(string="Date/time", required=True, default=lambda self: fields.Datetime.now())


    opening_data = fields.Float(string='Opening', required=True, default=0.0)
    closing_data = fields.Float(string='Closing', required=True, default=0.0)

    # data = fields.Float(string='Data', required=True, default=0.0)
    data = fields.Float(string='Consume', compute='_compute_data', store=True)

    meter_photo = fields.Image("Photo", max_width=800, max_height=800)

    @api.onchange('meter_id')
    def _onchange_meter_id_set_opening(self):
        for record in self:
            if record.meter_id:
                last_data = self.env['hms.meter.data'].search([
                    ('meter_id', '=', record.meter_id.id)
                ], order='data_datetime desc', limit=1)

                if last_data:
                    record.opening_data = last_data.closing_data or 0.0
                else:
                    record.opening_data = 0.0

    @api.model
    def create(self, vals):
        meter_id = vals.get('meter_id')
        data_datetime = vals.get('data_datetime')

        if meter_id and data_datetime and not vals.get('opening_data'):
            # Find the latest earlier data entry for the same meter
            previous_data = self.env['hms.meter.data'].search([
                ('meter_id', '=', meter_id),
                ('data_datetime', '<', data_datetime)
            ], order='data_datetime desc', limit=1)

            if previous_data:
                vals['opening_data'] = previous_data.closing_data or 0.0
            else:
                vals['opening_data'] = 0.0

        ret = super().create(vals)

        # if it is the latest data - switch off is_data_needed
        if ret and ret.meter_id.latest_data_id == ret:
            ret.meter_id.write({'is_data_needed': False})

        return ret

    @api.depends('opening_data' , 'closing_data')
    def _compute_data(self):
        for record in self:
            if record.closing_data:
                record.data = record.closing_data - record.opening_data