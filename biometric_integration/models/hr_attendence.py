from odoo.tools.safe_eval import pytz

from odoo import models, api, fields
from datetime import datetime, time, timedelta

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    is_single_punch = fields.Boolean(string='Single Punch?',default=False)

    @api.model
    def set_missing_checkout(self):
        # Get all attendance records for today without a checkout
        today = datetime.now().date()
        attendances = self.search([
            ('check_in', '>=', f'{today} 00:00:00'),
            ('check_in', '<=', f'{today} 23:59:59'),
            ('check_out', '=', False),
        ])

        # Inside your method where you handle attendance
        for attendance in attendances:
            try:
                employee_tz = attendance.employee_id.tz or 'UTC'
                employee_tz = pytz.timezone(employee_tz)

                # Get today's date
                today = fields.Date.context_today(self)

                # Create a naive checkout time using the employee's checkout setting
                checkout_time_naive = datetime.combine(today,
                                                       (datetime.min + timedelta(
                                                           hours=int(
                                                               attendance.employee_id.resource_calendar_id.checkout_time_for_single_punch),
                                                           minutes=int((
                                                                                   attendance.employee_id.resource_calendar_id.checkout_time_for_single_punch % 1) * 60))).time())

                # Localize the naive checkout time to the employee's timezone
                punch_time_local = employee_tz.localize(checkout_time_naive)

                # Convert to UTC
                checkout_time_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)

                # Write the naive datetime to the attendance record
                attendance.write({'check_out': checkout_time_utc,'is_single_punch':True})
            except Exception as e:
                attendance.message_post(body=f"Attendance single punch update error! \n Error: {str(e)}")