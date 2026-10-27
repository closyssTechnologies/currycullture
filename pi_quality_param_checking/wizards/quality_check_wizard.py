# -*- coding: utf-8 -*-
import ast

from odoo import api, fields, models, _
from odoo.addons.test_impex.tests.test_load import values
from odoo.exceptions import UserError
from odoo.http import request


class InheritedQualityCheckWizard(models.TransientModel):
    _inherit = 'quality.check.wizard'

    def _default_update_path(self):
        context = self.env.context
        # pass
        quality_check = request.env['quality.check'].browse(context['default_current_check_id'])
        values = []
        for parameter in quality_check.ccl_parameter_ids:
            values.append(self.env['wizard.quality.check.parameter'].create({
                # 'quality_check_wiz_id': rec.id,
                'parameter_id': parameter.parameter_id.id,
                'type_id': parameter.type_id.id,
                'range': parameter.range,
                'result': parameter.result,
                'remarks': parameter.remarks,
                'visibility': parameter.visibility,
            }).id)
        return values

    quality_check_param_ids = fields.One2many(
        'wizard.quality.check.parameter',
        'quality_check_wiz_id',
        string='CCL Parameters',
        default= _default_update_path
    )

    @api.depends('current_check_id', 'check_ids')
    def _compute_quality_checks(self):
        for rec in self:
            quality_check = request.env['quality.check'].browse(rec.current_check_id)
            for parameter in quality_check.ccl_parameter_ids:
                self.env['wizard.quality.check.parameter'].create({
                    'quality_check_wiz_id': rec.id,
                    'parameter_id': parameter.parameter_id.id,
                    'type_id': parameter.type_id.id,
                    'range': parameter.range,
                    'result': parameter.result,
                    'remarks': parameter.remarks,
                    'visibility': parameter.visibility,
                })

    # def do_pass(self):
    #     res = super().do_pass()
    #     return res
    #
    # def do_fail(self):
    #     res = super().do_fail()
    #     return res
    #
    # def confirm_fail(self):
    #     res = super().confirm_fail()
    #     return res
    def write(self, vals):

        res = super(InheritedQualityCheckWizard, self).write(vals)
        quality_check = self.env['quality.check'].browse(vals.get('current_check_id'))

        if quality_check:
            for parameter in quality_check.ccl_parameter_ids:
                # Find the corresponding record to update
                existing_param = self.env['quality.check.parameter'].search([
                    ('quality_check_id', '=', quality_check.id),
                    ('parameter_id', '=', parameter.parameter_id.id)
                ], limit=1)

                # Update fields if the record exists
                if existing_param:
                    existing_param.write({
                        'result': parameter.result,
                        'remarks': parameter.remarks,
                        'visibility': parameter.visibility,
                    })

        return res



    def create(self, val_list):
        # Create the quality check record
        quality_check_wiz = super(InheritedQualityCheckWizard, self).create(val_list)
        if 'current_check_id' in val_list and val_list.get('current_check_id', False):
            quality_check = self.env['quality.check'].browse(val_list['current_check_id'])

        # Check if a quality point is linked and copy its parameters
        if 'current_check_id' in val_list and val_list.get('current_check_id',False):
            quality_check = self.env['quality.check'].browse(val_list['current_check_id'])

            for parameter in quality_check_wiz.quality_check_param_ids:
                # Find the corresponding record to update
                existing_param = quality_check.ccl_parameter_ids.search([
                    ('quality_check_id', '=', quality_check.id),
                    ('parameter_id', '=', parameter.parameter_id.id)
                ], limit=1)

                # Update fields if the record exists
                if existing_param:
                    existing_param.write({
                        'result': parameter.result,
                        'remarks': parameter.remarks,
                        'visibility': parameter.visibility,
                    })

            # for parameter in quality_check.ccl_parameter_ids:
            #     self.env['wizard.quality.check.parameter'].create({
            #         'quality_check_wiz_id': quality_check_wiz.id,
            #         'parameter_id': parameter.parameter_id.id,
            #         'type_id': parameter.type_id.id,
            #         'range': parameter.range,
            #         'result': parameter.result,
            #         'remarks': parameter.remarks,
            #         'visibility': parameter.visibility,
            #     })

        return quality_check_wiz

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

