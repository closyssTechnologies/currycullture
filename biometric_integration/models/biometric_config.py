import random
from datetime import datetime, timedelta
from json import JSONDecodeError

import odoo.exceptions
from odoo import api, fields, models, _, SUPERUSER_ID, exceptions
import requests




def _create_biometric_company_user(res_record):
    # Generate the db_name with a random number
    base_db = res_record.env['ir.config_parameter'].sudo().get_param('biometric_integration.biometric_configure_db_name') if res_record.env['ir.config_parameter'].sudo().get_param('biometric_integration.biometric_configure_db_name') else res_record.env.cr.dbname
    db_name = f"{base_db}_{random.randint(1000, 9999)}"

    # Prepare the request body
    request_body = {
        "code": db_name,
        "name": db_name,
        "contact": res_record.env.user.phone or "",
        "emailID": res_record.env.user.email or "",
        "remarks": "",
        "faceRequired": True,
        "userID": "1",  # Use the field from the model
        "userName": '1',  # Assuming username is the same as userID
    }

    # Define the API endpoint
    api_endpoint = f"{res_record.env['ir.config_parameter'].sudo().get_param('biometric_integration.biometric_configure_base_url')}/api/Company/AddNewCompanyWithUserAuthToken"

    # Send the request to the biometric system API
    response = requests.post(api_endpoint, json=request_body)

    # Check the response from the API
    if response.status_code == 200:
        updated_response = response.json()
        updated_response['code']=db_name
        return updated_response
    else:
        raise odoo.exceptions.UserError(f"Biometric API request failed: {response.raise_for_status()}\nResponse Text: {response.text}")

        # response.raise_for_status()

class BiometricConfig(models.Model):
    _name = 'biometric.config'
    _rec_name = 'bio_company_name'
    _inherit = ['mail.thread']
    _description = 'BioSync Biometric Config'

    biometric_configure_auth_token = fields.Char(string="Auth Token")
    bio_company_name = fields.Char(string='BioSync Biometric Company Name',readonly=True)
    bio_company_id = fields.Char(string='BioSync Biometric Company ID')
    bio_company_code = fields.Char(string='BioSync Biometric Company Code')

    device_count = fields.Integer("Devices", compute='_compute_device_count')
    groups_count = fields.Integer("Groupts", compute='_compute_groups_count')
    attendance_count = fields.Integer(string='Attendance Count',compute='_compute_attendance_count')
    hr_attendance_count = fields.Integer(string='Hr attendance Count',compute='_compute_hr_attendance_count')
    employee_count = fields.Integer(string='Employee Count',compute='_compute_biometric_employee_count')
    device_ids = fields.One2many('biometric.device', 'bio_company_id', string='Device IDs')

    attendance_inout_mode = fields.Selection([("10","10"),("11_12","11 & 12")],default="11_12")
    attendance_inout_type = fields.Selection([("odd_even","Odd & Even Sync"),("first_last","First & Last Sync")])

    @api.onchange("attendance_inout_mode")
    def _onchange_attendance_inout_mode(self):
        for record in self:
            if record.attendance_inout_mode == "11_12":
                record.attendance_inout_type = None

    def _compute_device_count(self):
        for rec in self:
            rec.device_count = len(self.env["biometric.device"].search([('bio_company_id', '=', self.id)]))
    def _compute_biometric_employee_count(self):
        for rec in self:
            rec.employee_count = len(self.env["hr.employee"].search([('biometric_group_id', '!=', None)]))

    def _compute_groups_count(self):
        for rec in self:
            # rec.groups_count = len(self.env["biometric.ou"].search([('bio_company_id', '=', self.id)]))
            rec.groups_count = len(self.env["biometric.ou"].search([]))


    def _compute_attendance_count(self):
        for rec in self:
               rec.attendance_count = len(self.env['biometric.attendance.log'].search([]))

    def action_open_attendance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance',
            'view_mode': 'tree,form',
            'res_model': 'biometric.attendance.log',

            'context': dict(self.env.context, create=False),
        }

    def _compute_hr_attendance_count(self):
            for rec in self:
                #rec.hr_attendance_count = len(self.env['hr.attendance'].search([('Mode', '=', 'biometric_device')]))
                rec.hr_attendance_count = len(self.env['hr.attendance'].sudo().search([
                    ('in_mode', '=', 'biometric_device'),
                ]))

    def action_open_hr_attendance(self):

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance',
            'view_mode': 'tree,form',
            'res_model': 'hr.attendance',
            'domain' : [('in_mode','=','biometric_device')],
            'context': dict(self.env.context, create=False),
        }
    def _compute_group_employee_count(self):
            for rec in self:
                #rec.hr_attendance_count = len(self.env['hr.attendance'].search([('Mode', '=', 'biometric_device')]))
                rec.employee_count = len(self.env['hr.employee'].search([
                    ('biometric_group_id', '!=', False),
                ]))
    def action_open_hr_employee(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'HrAttendance',
            'view_mode': 'tree',
            'res_model': 'hr.employee',
            'domain': [('biometric_group_id', '!=', False)],
            'context': dict(self.env.context,create=False),
            'target': 'current',
        }







    @api.model
    def open_first_record(self):
        first_record = self.search([], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Biometric Config',
            'res_model': 'biometric.config',
            'view_mode': 'form',
            'res_id': first_record.id if first_record else False,
            'target': 'current',
        }

    def action_open_device_list(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Device List"),
            "res_model": "biometric.device",
            "views": [[False, "tree"], [False, "form"]],
            "context": {
                "create": 0
            },
            "domain": [('bio_company_id', '=', self.id)]
        }
    def action_open_group_list(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Group(OU) List"),
            "res_model": "biometric.ou",
            "views": [[False, "tree"], [False, "form"]],
            "context": {
                "create": 0
            },
            # "domain": [('bio_company_id', '=', self.id)]
        }

    def _check_biometric_credentials_user(self):
        error = ""
        if not self.env['ir.config_parameter'].sudo().get_param('biometric_integration.biometric_configure_base_url'):
            error += "\nNo Base URL provided."

        if error:
            raise exceptions.UserError(error)

    def register_new_company(self):
        """
            Register new company with user Auth token

        """
        for record in self:
            record._check_biometric_credentials_user()
            exist_company = self.search(
                # [('bio_company_code', 'ilike', record.env.cr.dbname)]) # No need
                []) # No need
            if len(exist_company)>1:
                raise odoo.exceptions.UserError("Only one config")
            try:
                bio_company_data = _create_biometric_company_user(record)
                if bio_company_data:
                    record.write({
                        "bio_company_name": bio_company_data.get("code", ""),
                        "bio_company_code": bio_company_data.get("code", ""),
                        "biometric_configure_auth_token": bio_company_data.get("authToken", ""),
                    })
            except Exception as e:
                raise exceptions.UserError(f"Error creating biometric company: {str(e)}")

    def get_auth_token(self):
        try:
            params={
                "UserID": 1,
                "Password": "1234",
                "CompanyCode": self.bio_company_name

            }
            auth_token = self.action_biometric_integration_api_call(method="GET", params=params,
                                                                                endpoint="/api/User/GetAuthTokenByUser")

            self.biometric_configure_auth_token = auth_token.get("authToken")
        except Exception as e:
            raise odoo.exceptions.UserError(str(e))


    def action_open_device_assignment(self):
        """
            Action button Open Device Assignment

        """
        try:
            self.get_auth_token()
            unassigned_device_list =self.action_biometric_integration_api_call(method="GET", params={},endpoint="/api/Device/GetUnassignedDevice")
            if unassigned_device_list:
                un_ass_device_to_create = []
                for device in unassigned_device_list:
                    exist_device = self.env['biometric.device'].search([("cpuid","=",device['cpuid'])],limit=1)
                    if not exist_device:
                        un_ass_device_to_create.append({
                            "cpuid": device.get('cpuid'),
                            "device_name": device.get('cpuid',""),
                            "device_ip": device.get('ipAddress',""),
                            "sub_type": device.get('subType',""),
                        })
                    else:
                        exist_device.write({
                            "cpuid": device.get('cpuid'),
                            "device_name": device.get('cpuid', ""),
                            "device_ip": device.get('ipAddress', ""),
                            "sub_type": device.get('subType', ""),
                            "bio_company_id": None,
                            "ou_code": None,
                        })


                if un_ass_device_to_create:
                    self.env['biometric.device'].create(un_ass_device_to_create)
        except Exception as e:
            raise odoo.exceptions.UserError(str(e))
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'res_model': 'wizard.device.assignment',
            "name": _("Device assignment"),
            "context": {
                "default_biometric_config_id": self.id
            },
            "target": "new",
        }

    def action_open_add_group(self):
        """
            Action button add group

        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'res_model': 'biometric.group.wizard',
            "name": _("Add groups"),
            "context": {
                "default_biometric_config_id": self.id
            },
            "target": "new",
        }
    ###################################################################################
        # Add
    ###################################################################################

    ###################################################################################
                        # API Calls
    ###################################################################################
        # ===================================================================
        """
            Common api call for Biometric Integration
        """

    def action_biometric_integration_api_call(self, method, params, endpoint, payload={},
                                              need_authtoken_param=False, need_authtoken_payload=False,need_authtoken_header=False):
        if not self.env['ir.config_parameter'].sudo().get_param('biometric_integration.biometric_configure_base_url'):
            raise odoo.exceptions.UserError("No Base URL found!")
        if need_authtoken_param:
            params.update({
                "AuthToken": self.biometric_configure_auth_token
            })
        headers = {}
        if need_authtoken_header:
            headers.update({
                "AuthToken": self.biometric_configure_auth_token
            })
        if need_authtoken_payload:
            payload.update({
                "authToken": self.biometric_configure_auth_token
            })
        api_endpoint = f"{self.env['ir.config_parameter'].sudo().get_param('biometric_integration.biometric_configure_base_url') + endpoint}"

        # Send the request to the biometric system API
        response = requests.request(method=method,headers=headers, params=params, url=api_endpoint, json=payload)

        # Check the response from the API
        if response.status_code == 200:
            try:
#                 data ={
#   "message": "Success",
#   "isSucceed": True,
#   "items": [
#     {
#       "cpuid": "6728423070000328",
#       "idNo": "00000001",
#       "empNo": "14",
#       "name": "",
#       "punchTime": "2024-08-17T14:47:57",
#       "strPunchTime": "17-Aug-2024 02:47 PM",
#       "ouCode": "",
#       "inOutMode": "10"
#     },
#     {
#       "cpuid": "6728423070000328",
#       "idNo": "00000001",
#       "empNo": "14",
#       "name": "",
#       "punchTime": "2024-08-17T14:48:07",
#       "strPunchTime": "17-Aug-2024 02:48 PM",
#       "ouCode": "",
#       "inOutMode": "10"
#     },
#     {
#       "cpuid": "6728423070000328",
#       "idNo": "00000001",
#       "empNo": "14",
#       "name": "",
#       "punchTime": "2024-08-17T14:48:10",
#       "strPunchTime": "17-Aug-2024 02:48 PM",
#       "ouCode": "",
#       "inOutMode": "10"
#     },
#     {
#       "cpuid": "6728423070000328",
#       "idNo": "00000001",
#       "empNo": "14",
#       "name": "",
#       "punchTime": "2024-08-17T14:48:14",
#       "strPunchTime": "17-Aug-2024 02:48 PM",
#       "ouCode": "",
#       "inOutMode": "10"
#     }
#   ]
# }
#                 return data
                return response.json()
            except JSONDecodeError:
                return response.text
        else:
            raise odoo.exceptions.UserError(
                f"Biometric API request failed: {response.status_code}\nResponse Text: {response.text}")

            # response.raise_for_status()




    # ==========================[Ir Cron]==========================================
    def _cron_sync_company_device_status(self):
        try:
            bio_company_config = self.env['biometric.config'].search([],limit=1)
            params = {
                "code": self.bio_company_code, # Company Code

            }
            device_status = bio_company_config.action_biometric_integration_api_call( "GET", params, "/api/WebApi/StatusByCompanyCode", payload={},
                                              need_authtoken_param=False, need_authtoken_payload=False,need_authtoken_header=True)

            api_devices = device_status.get("items", [])

            # Iterate through each device in Odoo's one2many field
            for device in bio_company_config.device_ids:
                # Find the corresponding device from the API response using a unique identifier (e.g., device ID)
                try:
                    matching_device = next((d for d in api_devices if d.get("cpuid") == device.cpuid), None)

                    # If a matching device is found, update the status
                    if matching_device:
                        status = "offline"
                        provided_time = datetime.strptime(matching_device.get("lastSyncWithServer"), "%Y-%m-%dT%H:%M:%S.%f")
                        current_time = datetime.now()
                        time_difference = current_time - provided_time
                        if  time_difference < timedelta(minutes=int(self.env['ir.config_parameter'].sudo().get_param('biometric_integration.biometric_configure_device_sync_time_interval'))):
                            status = "online"

                        device.write({
                            'device_status': status,
                            # Assuming 'status' is a field in your device model
                            'device_last_sync': matching_device.get("lastSyncWithServer"),  # Optionally, update the last sync time
                        })
                    else:
                        device.write({
                            'device_status': "unavailable",
                        })
                except Exception as e:
                    continue

            print(device_status)

            # self.biometric_configure_auth_token = auth_token.get("authToken")
        except Exception as e:
            raise odoo.exceptions.UserError(str(e))


class BiometricDevice(models.Model):
    _name = 'biometric.device'
    _rec_name = "cpuid"
    _description = "Biometric Assigned Device"


    cpuid = fields.Char(string='CPUID')
    device_name = fields.Char(string='Device Name')
    bio_company_id = fields.Many2one('biometric.config', string='Biometric Company',ondelete='cascade')
    ou_code = fields.Many2one('biometric.ou',string='Biometric OU')
    device_ip = fields.Char(string='Device IP')
    device_status = fields.Selection([("online","Online"),("offline","Offline"),("unavailable","Unavailable")], string='Device Status')
    device_type = fields.Char(string='Device Type')
    device_last_sync = fields.Char(string='Device Last Sync')
    sub_type = fields.Char(string='Sub Type')

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.cpuid}"+"-Assigned" if self.bio_company_id else f"{record.cpuid}"+"-Unassigned"

# class BiometricUnassignnedDevice(models.Model):
#     _name = 'biometric.unassigned.device'
#     _rec_name = "cpuid"
#     _description = "Biometric Unassigned Device"
#
#
#     cpuid = fields.Char(string='CPUID')
#     device_name = fields.Char(string='Device Name')
#     bio_company_id = fields.Many2one('biometric.config', string='Biometric Company')
#     device_ip = fields.Char(string='Device IP')

class BiometricOU(models.Model):
    _name = 'biometric.ou'
    _rec_name = 'ou_code'
    _description = "Biometric OU"

    ouid = fields.Char(string='OU ID')
    bio_company_id = fields.Many2one('biometric.config', string='Biometric Company',ondelete='cascade')
    ou_name = fields.Char(string='OU Name')
    ou_code = fields.Char(string='OU Code')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            try:
                data = {
                    "ouName": vals.get("ou_code"),
                    "ouCode": vals.get("ou_code"),
                    "parentOUID": 0,
                    "contact": "",
                    "registerDate": "",
                }
                config_id = self.env['biometric.config'].search([],limit=1)
                config_id.get_auth_token()
                ou_group_create =config_id.action_biometric_integration_api_call(method="POST", params={},payload=data,endpoint="/api/OU/AddNewOU",need_authtoken_payload=True)
                print(ou_group_create)
                get_ou_info = config_id.action_biometric_integration_api_call(method="GET", params={},payload=data,endpoint="/api/OU/CompanyWiseOUDetails",need_authtoken_param=True)
                for ou in get_ou_info:
                    if ou["ouCode"] == vals.get("ou_code"):
                        ou_id = ou["ouid"]

                vals.update({"ouid":ou_id,"ou_name":vals.get("ou_code"),"ou_code": vals.get("ou_code"),"bio_company_id":config_id.id})
            except Exception as e:
                raise odoo.exceptions.UserError(str(e))
        return super(BiometricOU,self).create(vals_list)
