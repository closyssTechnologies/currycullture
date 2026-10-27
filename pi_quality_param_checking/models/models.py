from odoo import models, fields

class CCLParameter(models.Model):
    _name = 'ccl.parameter'
    _description = 'CCL Parameter'

    name = fields.Char(string='Parameter Name', required=True)

class CCLParameterType(models.Model):
    _name = 'ccl.parameter.type'
    _description = 'CCL Parameter Type'

    name = fields.Char(string='Type Name', required=True)

class QualityPoint(models.Model):
    _inherit = 'quality.point'

    ccl_parameter_ids = fields.One2many(
        'quality.point.parameter', 'quality_point_id', string='CCL Parameters'
    )

class QualityPointParameter(models.Model):
    _name = 'quality.point.parameter'
    _description = 'Quality Point Parameter'

    quality_point_id = fields.Many2one('quality.point', string='Quality Point')
    parameter_id = fields.Many2one('ccl.parameter', string='Parameter', required=True)
    type_id = fields.Many2one('ccl.parameter.type', string='Type', required=True)
    range = fields.Char(string='Range')
    result = fields.Char(string='Result')
    remarks = fields.Char(string='Remarks')
    visibility = fields.Boolean(string='Visible', default=True)


from odoo import models, fields, api


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    ccl_parameter_ids = fields.One2many(
        'quality.check.parameter', 'quality_check_id', string='CCL Parameters'
    )

    @api.model_create_multi
    def create(self, vals):
        # Create the quality check record
        quality_check = super(QualityCheck, self).create(vals)

        for quality_check_id in quality_check:
            # quality_point = self.env['quality.point'].browse(quality_check_id.point_id)
            quality_point = quality_check_id.point_id
            for parameter in quality_point.ccl_parameter_ids:
                self.env['quality.check.parameter'].create({
                    'quality_check_id': quality_check_id.id,
                    'parameter_id': parameter.parameter_id.id,
                    'type_id': parameter.type_id.id,
                    'range': parameter.range,
                    'result': parameter.result,
                    'remarks': parameter.remarks,
                    'visibility': parameter.visibility,
                })


        # # Check if a quality point is linked and copy its parameters
        # for value in vals:
        #     if 'point_id' in value and value['point_id']:
        #         quality_point = self.env['quality.point'].browse(value['point_id'])
        #         for parameter in quality_point.ccl_parameter_ids:
        #             self.env['quality.check.parameter'].create({
        #                 'quality_check_id': quality_check.id,
        #                 'parameter_id': parameter.parameter_id.id,
        #                 'type_id': parameter.type_id.id,
        #                 'range': parameter.range,
        #                 'result': parameter.result,
        #                 'remarks': parameter.remarks,
        #                 'visibility': parameter.visibility,
        #             })

        return quality_check


class QualityCheckParameter(models.Model):
    _name = 'quality.check.parameter'
    _description = 'Quality Check Parameter'

    quality_check_id = fields.Many2one('quality.check', string='Quality Check')
    parameter_id = fields.Many2one('ccl.parameter', string='Parameter', required=True)
    type_id = fields.Many2one('ccl.parameter.type', string='Type', required=True)
    range = fields.Char(string='Range')
    result = fields.Char(string='Result')
    remarks = fields.Char(string='Remarks')
    visibility = fields.Boolean(string='Visible', default=True)
