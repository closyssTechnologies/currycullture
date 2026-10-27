# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
_logger = logging.getLogger(__name__)


class HmsMeter(models.Model):
    _name = 'hms.meter'
    _description = 'HMS Meter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    _order = 'sequence, id desc'

    name = fields.Char(string='Meter name', required=True, help='ex. Hot water, Electricity, Gas')
    sequence = fields.Integer(default=10, index=True)
    code = fields.Char(string='Meter code', required=True, help='ex. Meter code or id written on it')

    unit_costing = fields.Float(string='Unit Costing', required=True, help='ex. Cost of per unit')

    meter_type_id = fields.Many2one(comodel_name='hms.meter.type', string='Meter type')

    meter_data_ids = fields.One2many('hms.meter.data', 'meter_id', string='Data of this meter')
    meter_data_count = fields.Integer("Data count", compute='_compute_data_count')

    latest_data_id = fields.Many2one(comodel_name='hms.meter.data', string='Latest consume record', compute='_compute_latest_data', store=True)
    latest_data_datetime = fields.Datetime(string="Latest Consume datetime", compute='_compute_latest_data', store=True)
    latest_data = fields.Float(string="Latest Consume", compute='_compute_latest_data', store=True)

    latest_closing_data = fields.Float(string="Latest closing", compute='_compute_latest_data', store=True)

    is_data_needed = fields.Boolean(string="Is data needed?", default=True, help="Is data needed?")

    active = fields.Boolean(default=True, help="Set active to false to hide the meter without removing it.")

    @api.depends('meter_data_ids', 'meter_data_ids.data_datetime', 'meter_data_ids.data')
    def _compute_latest_data(self):
        for m in self:
            latest_data_id = False
            if m.meter_data_ids:
                latest_data_id = m.meter_data_ids.sorted('data_datetime', True)[0]
            m.latest_data_id = latest_data_id
            m.latest_data_datetime = latest_data_id.data_datetime if latest_data_id else False
            m.latest_data = latest_data_id.data if latest_data_id else False
            m.latest_closing_data = latest_data_id.closing_data if latest_data_id else False

    def _compute_data_count(self):
        for m in self:
            m.meter_data_count = len(m.meter_data_ids)

    def action_view_data(self):
        self.ensure_one()

        ctx = dict(self.env.context)
        ctx.update({
            'default_meter_id': self.id,
        })

        return {
            'name': 'Meter data',
            'view_mode': 'tree,form',
            'res_model': 'hms.meter.data',
            'type': 'ir.actions.act_window',
            'domain': [('meter_id', '=', self.id)],
            'context': ctx
        }

    def toggle_needed(self):
        for record in self:
            record.write({'is_data_needed': not record.is_data_needed})

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        meter_id = self._context.get('default_meter_id')
        if meter_id:
            meter = self.env['hms.meter'].browse(meter_id)
            if 'opening_data' in fields:
                res['opening_data'] = meter.latest_closing_data or 0.0
        return res


