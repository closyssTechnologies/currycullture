from odoo import api, fields, models, _,exceptions
from odoo.addons.base.models.res_partner import _tz_get
from odoo.tools.safe_eval import pytz
from datetime import datetime


class DeviceAssignmentWizard(models.TransientModel):
    _name = 'wizard.device.assignment'
    _description = 'Device Assignment Wizard'



    unassigned_device_id = fields.Many2one('biometric.device', string='Unassigned Device')
    device_friendly_name = fields.Char(string='Device Friendly Name')
    device_tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),
                          help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
                               "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
                               "Anywhere else, time values are computed according to the time offset of your web client.")

    biometric_group = fields.Many2one('biometric.ou', string='Groups(OU)')
    biometric_config_id = fields.Many2one('biometric.config', string='Biometric Config')

    def get_timezone_offset(self,time_zone):
        tz = pytz.timezone(time_zone)
        now = datetime.now(tz)
        offset = now.strftime('%z')
        offset_hours = offset[:3]
        offset_minutes = offset[3:]
        formatted_offset = f"{offset_hours}:{offset_minutes}"
        return formatted_offset

    def assign_device_company_group(self):
        self.biometric_config_id.get_auth_token()
        if self.unassigned_device_id:
            try:
                if not self.unassigned_device_id.bio_company_id:
                    data = {
                        "companyCode": self.biometric_config_id.bio_company_code,
                        "deviceName": self.device_friendly_name,
                        "cpuid": self.unassigned_device_id.cpuid
                    }
                    self.env['biometric.config'].search([],limit=1).action_biometric_integration_api_call(method="POST",
                                                                                                                  params={},
                                                                                                                  payload=data,
                                                                                                                  endpoint="/api/Device/AddToCompany",
                                                                                                                  )
                    try:
                        timezone_add_data = {"CPUID" : self.unassigned_device_id.cpuid  , "TimeZoneHourMin" : self.get_timezone_offset(self.device_tz)}
                        self.env['biometric.config'].search([], limit=1).action_biometric_integration_api_call(
                            method="GET",
                            params=timezone_add_data,
                            payload={},
                            endpoint="/api/Device/TimeZoneByCPUID",
                            )
                    except Exception as e:
                        pass

                    self.unassigned_device_id.bio_company_id = self.biometric_config_id
                    self.unassigned_device_id.write({
                        "bio_company_id": self.biometric_config_id,
                        "device_name": self.device_friendly_name})

                # ================================ Device ADD TO OU ============================
                device_add_to_ou = {
                    "ID": self.unassigned_device_id.cpuid,
                    "Name": self.unassigned_device_id.device_name,
                    "OUCode": self.biometric_group.ou_code,
                    "OUName": self.biometric_group.ou_code
                }
                self.env['biometric.config'].search([],limit=1).action_biometric_integration_api_call(
                    method="POST",
                    params=device_add_to_ou,
                    payload={},
                    endpoint="/api/Device/AddToOU",
                    need_authtoken_param=True
                    )

                self.unassigned_device_id.ou_code = self.biometric_group
            except Exception as e:
                raise exceptions.UserError(str(e))





class AddBiometricGroup(models.TransientModel):
    _name = 'biometric.group.wizard'
    _description = 'Add Biometric Group Wizard'



    # biometric_group = fields.Many2one('biometric.ou', string='Groups(OU)')
    biometric_group_name = fields.Char('Biometric Group')
    biometric_config_id = fields.Many2one('biometric.config', string='Biometric Config')



    def create_group(self):
        try:
            self.env['biometric.ou'].create({"ouid": self.biometric_group_name, "ou_code":self.biometric_group_name})
        except Exception as e:
            raise exceptions.UserError(str(e))




