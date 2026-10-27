from odoo import models, fields, api,exceptions
from odoo.http import request

import requests
import random


# def _create_biometric_company(res_record):
#     # Generate the db_name with a random number
#     db_name = f"{res_record.env.cr.dbname}_{random.randint(1000, 9999)}"
#
#
#     # Prepare the request body
#     request_body = {
#         "code": db_name,
#         "name": db_name,
#         "contact": res_record.env.user.phone if res_record.env.user.phone else "",
#         "emailID": res_record.env.user.email if res_record.env.user.email else "",
#         # "address": None,
#         # "validupto": None,
#         "remarks": "",
#         "faceRequired": True,
#         "userID": 1,  # Assuming this is always '1' or you can change it dynamically
#         "userName": '1',# Assuming this is always '1' or you can change it dynamically
#         # 'active':True
#     }
#
#     # Define the API endpoint
#     # params = {"AuthToken": "c180118cbd3f3e09414770522b9008106a7a29b05de66499fe7e5b03eeb61c03"}
#     api_endpoint = f"{res_record.biometric_configure_base_url}/api/Company/AddNewCompanyWithUserAuthToken"
#
#     # Send the request to the biometric system API
#     response = requests.post(api_endpoint, json=request_body)
#
#     # Check the response from the API
#     if response.status_code == 200:
#         # api_endpoint = f"{res_record.biometric_configure_base_url}/api/Company/CompaniesByCode"
#         #
#         # param = db_name
#         # # Send the request to the biometric system API
#         # response = requests.get(api_endpoint,params=param)
#
#         return {"code":db_name}
#     else:
#         response.raise_for_status()




class PayrollResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    def _get_min_slection(self):
        return [(str(i),str(i))for i in range(1,61)]

    biometric_configure_base_url= fields.Char(store=True,config_parameter='biometric_integration.biometric_configure_base_url' ,default ="")
    biometric_configure_db_name = fields.Char(store=True,
                                               config_parameter='biometric_integration.biometric_configure_db_name',
                                               default="")

    biometric_configure_device_sync_time_interval = fields.Selection(lambda x: x._get_min_slection(),store=True,
                                              config_parameter='biometric_integration.biometric_configure_device_sync_time_interval',
                                              default='10')

    biometric_employee_id = fields.Selection([("employee_id","Employee ID"),("badge_id","Badge ID")], store=True,
                                                                     config_parameter='biometric_integration.biometric_employee_id',
                                                                     default="employee_id")