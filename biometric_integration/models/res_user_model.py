from json import JSONDecodeError

import odoo.exceptions
from odoo import models, fields, api, exceptions
import requests
import random

# def _create_biometric_company_user(res_record):
#     # Generate the db_name with a random number
#     db_name = f"{res_record.env.cr.dbname}_{random.randint(1000, 9999)}"
#
#     # Prepare the request body
#     request_body = {
#         "code": db_name,
#         "name": db_name,
#         "contact": res_record.env.user.phone or "",
#         "emailID": res_record.env.user.email or "",
#         "remarks": "",
#         "faceRequired": True,
#         "userID": res_record.biometric_configure_user_id,  # Use the field from the model
#         "userName": res_record.biometric_configure_user_id,  # Assuming username is the same as userID
#     }
#
#     # Define the API endpoint
#     api_endpoint = f"{res_record.biometric_configure_base_url}/api/Company/AddNewCompany"
#
#     # Send the request to the biometric system API
#     response = requests.post(api_endpoint, json=request_body)
#
#     # Check the response from the API
#     if response.status_code == 200:
#         return {"code": db_name}
#     else:
#         raise odoo.exceptions.UserError(f"Biometric API request failed: {response.raise_for_status()}\nResponse Text: {response.text}")
#
#         # response.raise_for_status()

class ResUsers(models.Model):
    _inherit = 'res.users'

    biometric_configure_user_id = fields.Char(string="Biometric User ID")
    biometric_configure_password = fields.Char(string="Biometric Password")
    biometric_configure_company_code = fields.Char(string="Company Code")
    biometric_configure_auth_token = fields.Char(string="Auth Token")
    biometric_configure = fields.Boolean(string="Enable Biometric Integration")
    biometric_configure_base_url = fields.Char(string="Base URL")  # Ensure this field is correctly defined

    def _check_biometric_credentials_user(self):
        error = ""
        if not self.biometric_configure_user_id:
            error += "\nNo user ID provided."
        if not self.biometric_configure_password:
            error += "\nNo password provided."
        if not self.biometric_configure_company_code:
            error += "\nNo Company Code provided."

        if error:
            raise exceptions.UserError(error)

    @api.onchange("biometric_configure")
    def _onchange_create_biometric_config(self):
        for record in self:
            if record.biometric_configure:
                record._check_biometric_credentials_user()
                exist_company = self.env['biometric.config'].search([], limit=1).sudo().search(
                    [('bio_company_code', 'ilike', record.env.cr.dbname)])
                if exist_company:
                    return
                try:
                    bio_company_data = _create_biometric_company_user(record)
                    if bio_company_data:
                        self.env['biometric.config'].create({
                            "bio_company_name": bio_company_data.get("code", ""),
                            "bio_company_code": bio_company_data.get("code", ""),
                        })
                except Exception as e:
                    raise exceptions.UserError(f"Error creating biometric company: {str(e)}")
                record.biometric_configure = True




    """
        Get Auth token
    """
    def action_biometric_get_token(self):
        try:
            params = {
                # "UserID": 1
                # "Password": 1234
                # "CompanyCode": code

            }
            ou_group_create = self.env['res.users'].search([("biometric_configure", "=", True)],
                                                           limit=1).action_biometric_integration_api_call(method="POST",
                                                                                                          params={},
                                                                                                          payload=params,
                                                                                                          endpoint="/api/OU/AddNewOU",
                                                                                                          need_authtoken_payload=True)
            print(ou_group_create)
            # vals.update({"ou_code": vals.get("ouid")})

        except Exception as e:
            raise odoo.exceptions.UserError(str(e))