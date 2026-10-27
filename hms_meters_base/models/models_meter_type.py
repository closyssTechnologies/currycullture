# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)


class HmsMeterType(models.Model):
    _name = 'hms.meter.type'
    _description = 'HMS Meter Type'

    name = fields.Char(string='Meter type', required=True, help='ex. Water, Electricity, Gas')
    meter_ids = fields.One2many('hms.meter', 'meter_type_id', string='Meters of this type')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Type name already exists')
    ]

    def init(self):
        """Ensure default meter types are created if they do not exist."""
        meter_types = ['Electricity', 'Gas', 'Water']
        for meter_type in meter_types:
            self.env.cr.execute("""
                INSERT INTO hms_meter_type (name)
                SELECT %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM hms_meter_type WHERE name = %s
                );
            """, (meter_type, meter_type))

