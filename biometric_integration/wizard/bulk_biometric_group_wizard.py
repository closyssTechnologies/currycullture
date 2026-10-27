import logging

from odoo import api, fields, models, _,exceptions
_logger = logging.getLogger(__name__)

class BulkBiometricGroupWizard(models.TransientModel):
    _name = 'bulk.biometric.group.wizard'
    _description = 'Bulk Biometric Group Wizard'


    biometric_group = fields.Many2one('biometric.ou', string='Groups(OU)')
    employee_ids = fields.Many2many('hr.employee', string='Employees')


    def assign_employee_to_group(self):
        for employee in self.employee_ids:
            employee.biometric_group_id = self.biometric_group
            try:
                employee.create_biometric_employee()
            except Exception as e:
                employee.message_post(body="Group assignment failed!\n Reason:"+str(e))
                employee.biometric_group_id = None
