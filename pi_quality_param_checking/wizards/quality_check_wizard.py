# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InheritedQualityCheckWizard(models.TransientModel):
    _inherit = 'quality.check.wizard'

    def _default_update_path(self):
        check_id = self.env.context.get('default_current_check_id')
        if not check_id:
            return []
        quality_check = self.env['quality.check'].browse(check_id)
        values = []
        for parameter in quality_check.ccl_parameter_ids:
            wiz_param = self.env['wizard.quality.check.parameter'].create({
                'parameter_id': parameter.parameter_id.id,
                'type_id': parameter.type_id.id,
                'range': parameter.range,
                'result': parameter.result,
                'remarks': parameter.remarks,
                'visibility': parameter.visibility,
            })
            values.append(wiz_param.id)
        return values

    quality_check_param_ids = fields.One2many(
        'wizard.quality.check.parameter',
        'quality_check_wiz_id',
        string='CCL Parameters',
        default=_default_update_path
    )

    def write(self, vals):
        res = super(InheritedQualityCheckWizard, self).write(vals)
        check_id = vals.get('current_check_id')
        if check_id:
            quality_check = self.env['quality.check'].browse(check_id)
            if quality_check:
                for parameter in quality_check.ccl_parameter_ids:
                    existing_param = self.env['quality.check.parameter'].search([
                        ('quality_check_id', '=', quality_check.id),
                        ('parameter_id', '=', parameter.parameter_id.id)
                    ], limit=1)
                    if existing_param:
                        existing_param.write({
                            'result': parameter.result,
                            'remarks': parameter.remarks,
                            'visibility': parameter.visibility,
                        })
        return res

    @api.model_create_multi
    def create(self, val_list):
        records = super(InheritedQualityCheckWizard, self).create(val_list)
        for wiz, vals in zip(records, val_list):
            check_id = vals.get('current_check_id')
            if check_id:
                quality_check = self.env['quality.check'].browse(check_id)
                for parameter in wiz.quality_check_param_ids:
                    existing_param = quality_check.ccl_parameter_ids.search([
                        ('quality_check_id', '=', quality_check.id),
                        ('parameter_id', '=', parameter.parameter_id.id)
                    ], limit=1)
                    if existing_param:
                        existing_param.write({
                            'result': parameter.result,
                            'remarks': parameter.remarks,
                            'visibility': parameter.visibility,
                        })
        return records


class QualityCheckParameter(models.TransientModel):
    _name = 'wizard.quality.check.parameter'
    _description = 'Wizard Quality Check Parameter'

    quality_check_wiz_id = fields.Many2one('quality.check.wizard', string='Quality Check')
    parameter_id = fields.Many2one('ccl.parameter', string='Parameter', required=True)
    type_id = fields.Many2one('ccl.parameter.type', string='Type', required=True)
    range = fields.Char(string='Range')
    result = fields.Char(string='Result')
    remarks = fields.Char(string='Remarks')
    visibility = fields.Boolean(string='Visible', default=True)
