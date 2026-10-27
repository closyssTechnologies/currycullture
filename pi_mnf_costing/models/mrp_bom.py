from odoo import models, fields, api
from datetime import datetime
import calendar

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_category_id = fields.Many2one(
        'mrp.bom.category',
        string='BOM Category'
    )


    def init(self):
        """Ensure default meter types are created if they do not exist."""
        mo_types = ['SFB (Work-In-Progress)', 'PB (Packaging BOM)', 'MB (Manufacturing BOM)']
        for mo_type in mo_types:
            self.env.cr.execute("""
                INSERT INTO mrp_bom_category (name)
                SELECT %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM mrp_bom_category WHERE name = %s
                );
            """, (mo_type, mo_type))