import base64

from odoo import api, fields, models, _, exceptions, Command
from odoo.addons.test_convert.tests.test_env import record
from datetime import datetime


class InheritedHrEmployee(models.Model):
    _inherit = 'hr.employee'


    biometric_group_id = fields.Many2one(string="Biometric Group Name",comodel_name= "biometric.ou",groups="hr.group_hr_user")

    def get_image_base64(self):
        # Access the employee's image
        image_data = self.image_1920  # Replace with the appropriate field if necessary

        if not image_data:
            raise exceptions.UserError("No image found for this employee!")

        # Convert binary image data to Base64
        # image_base64 = base64.b64encode(image_data).decode('utf-8')
        # data = image_data.read()
        # image_base64 = data.decode("utf-8")

        return image_data.decode("utf-8")
    def create_biometric_employee(self):
        for record in self:
            try:
                self.env['biometric.config'].search([], limit=1).sudo().get_auth_token()
                employee_id_type = self.env['ir.config_parameter'].sudo().get_param('biometric_integration.biometric_employee_id')
                employee_no = str(record.id)
                if employee_id_type== "badge_id":
                    if not record.barcode:
                        raise exceptions.UserError("No Badge ID found for this employee!")
                    employee_no = str(record.barcode)

                data = {
                    "name": record.name,
                    "email": record.work_email,
                    "empNo": str(employee_no),
                    "cardNo": str(employee_no),
                    "ou": record.biometric_group_id.ou_code,
                    "idNo": str(employee_no),
                    "empImageBase64": self.get_image_base64(),
                }
                employee_registration = self.env['biometric.config'].search([],
                                                           limit=1).action_biometric_integration_api_call(method="POST",
                                                                                                          params={},
                                                                                                          payload=data,
                                                                                                          endpoint="/api/EmployeeRequest/AddEmployeeWithImage",
                                                                                                          need_authtoken_header=True)
                record.message_post(body=f"Employee Registration done. ID: {employee_no}")
            except Exception as e:
                raise exceptions.UserError(str(e))

    def action_open_group_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Assign Employees to group"),
            "res_model": "bulk.biometric.group.wizard",
            "views": [[False, "form"]],
            "context": {
                "default_employee_ids": [Command.link(id) for id in self.env.context.get('active_ids')]
            },
            "target": "new",
            # "domain": [('bio_company_id', '=', self.id)]
        }

    def write(self, vals):
        # Check if the record is being archived (i.e., active is being set to False)
        if 'active' in vals and not vals['active']:
            # Perform your custom logic here
            for record in self:
                # Example: Logging an action
                if record.biometric_group_id:
                    record.action_employee_inactive()
                # You can also trigger other actions, like sending an email, updating related records, etc.

        # Call the parent method to ensure the original behavior is preserved
        return super(InheritedHrEmployee, self).write(vals)

    def action_employee_inactive(self):
        for record in self:
            try:
                bio_company_config = self.env['biometric.config'].search([], limit=1)
                employee_id_type = self.env['ir.config_parameter'].sudo().get_param(
                    'biometric_integration.biometric_employee_id')
                employee_no = str(record.id)
                if employee_id_type == "badge_id":
                    if not record.barcode:
                        raise exceptions.UserError("No Badge ID found for this employee!")
                    employee_no = str(record.barcode)
                payload = {
                        "employeeNo":employee_no,
                        "cardNo": employee_no,
                        "name": record.name,
                        "ou": record.biometric_group_id.ou_code
                    }


                bio_company_config.get_auth_token()
                employee_inactive_response = bio_company_config.action_biometric_integration_api_call("POST", {},
                                                                                         "/api/EmployeeRequest/TagEmployeeAsInactive",
                                                                                         payload=payload,
                                                                                         need_authtoken_param=False,
                                                                                         need_authtoken_payload=False,
                                                                                         need_authtoken_header=True)

                if not employee_inactive_response.get( "isSucceed"):
                    raise exceptions.UserError("Employee Inactive is not succeed .Please contact with administrator.")

                record.biometric_group_id = None




                # self.biometric_configure_auth_token = auth_token.get("authToken")
            except Exception as e:
                raise exceptions.UserError(str(e))
