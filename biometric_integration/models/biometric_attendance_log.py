import logging
from datetime import datetime, timedelta

from odoo import api, fields, models, _, exceptions
from odoo.tools.safe_eval import pytz

_logger = logging.getLogger(__name__)


class InheritedHrAttendance(models.Model):
    _inherit = "hr.attendance"

    in_mode = fields.Selection(selection_add=[
        ('biometric_device', 'Biometric Device'),
    ], ondelete={'biometric_device': 'set default'})
    in_biometric_device = fields.Many2one(string="Biometric Device", comodel_name="biometric.device")
    out_mode = fields.Selection(selection_add=[
        ('biometric_device', 'In Biometric Device'),
    ], ondelete={'biometric_device': 'set default'})
    out_biometric_device = fields.Many2one(string="Out Biometric Device", comodel_name="biometric.device")


class BiometricAttendanceLog(models.Model):
    _name = 'biometric.attendance.log'
    _description = 'Biometric Attendance Log'
    _rec_name = 'name'

    device_id = fields.Char(string='Device ID')
    emp_no = fields.Char(string='Employee Number')
    card_id = fields.Char(string='Card ID')
    punch_time = fields.Char(string='Punch Time')
    name = fields.Char(string='Name')
    is_odoo_synced = fields.Boolean(string='Is Odoo Synced?', default=False)
    inout_mode = fields.Char(string='Inout Mode')
    employee_id = fields.Many2one('hr.employee',string='Employee')


    def _check_frequent_log(self,item):
        punch_time_str = item.get("punchTime", "")
        punch_time = datetime.strptime(punch_time_str, "%Y-%m-%dT%H:%M:%S")

        # Fetch the latest record for the employee
        recent_records = self.search([
            ('emp_no', '=', item.get("empNo", ""))
        ], order="id desc", limit=10)  # Limit to a small number of recent records

        # Convert and sort the recent records by punch_time
        recent_records_sorted = sorted(
            recent_records,
            key=lambda r: datetime.strptime(r.punch_time, "%Y-%m-%dT%H:%M:%S"),
            reverse=True  # Sort in descending order
        )

        # Get the most recent punch time record
        last_record = recent_records_sorted[0] if recent_records_sorted else None

        if last_record:
            # Convert last punch time to datetime
            last_punch_time = datetime.strptime(last_record.punch_time, "%Y-%m-%dT%H:%M:%S")

            # Calculate the time difference
            time_difference = punch_time - last_punch_time
            if time_difference.total_seconds() <= 300:
                # If within 10 seconds, do not create a new record
                return  True

    def _cron_sync(self):

        try:
            self.env['biometric.config'].search([], limit=1).sudo().get_auth_token()
            get_unsync_att = self.env['biometric.config'].search([], limit=1).action_biometric_integration_api_call(
                method="GET",
                params={},
                endpoint="/api/WebApi/GetUnSyncAttendanceData",
                need_authtoken_header=True)

            # get_unsync_att = {'isSucceed': True, 'items': [
            #     {'cpuid': '6728423070000328', 'empNo': 'PIEI0104', 'idNo': 'PIEI0104', 'inOutMode': '10', 'name': '',
            #      'ouCode': '', 'punchTime': '2024-09-21T12:57:03', 'strPunchTime': '21-Sep-2024 12:57 PM'},
            #     {'cpuid': '6728423070000328', 'empNo': 'PIEI0121', 'idNo': 'PIEI0121', 'inOutMode': '10', 'name': '',
            #      'ouCode': '', 'punchTime': '2024-09-21T12:57:37', 'strPunchTime': '21-Sep-2024 12:57 PM'}],
            #  'message': 'Success'}
            # get_unsync_att = {'isSucceed': True, 'items': [
            #     {'cpuid': '6728423070000328', 'empNo': 'PIEI0104', 'idNo': 'PIEI0104', 'inOutMode': '10', 'name': '',
            #      'ouCode': '', 'punchTime': '2024-09-21T14:57:03', 'strPunchTime': '21-Sep-2024 14:57 PM'},
            #     {'cpuid': '6728423070000328', 'empNo': 'PIEI0121', 'idNo': 'PIEI0121', 'inOutMode': '10', 'name': '',
            #      'ouCode': '', 'punchTime': '2024-09-21T14:57:37', 'strPunchTime': '21-Sep-2024 14:57 PM'}],
            #  'message': 'Success'}

            if get_unsync_att.get("items", False):
                data_list = []
                for item in get_unsync_att.get("items"):
                    if self.search([('device_id', '=', item.get("cpuid", "")), ('emp_no', '=', item.get("empNo", "")),
                                    ('punch_time', '=', item.get("punchTime", "")),
                                    ('name', '=', item.get("name", ""))]).exists():
                        continue


                    if self._check_frequent_log(item):
                        continue

                    employee_id_type = self.env['ir.config_parameter'].sudo().get_param(
                        'biometric_integration.biometric_employee_id')
                    if employee_id_type == 'badge_id':
                        employee_id = self.env['hr.employee'].sudo().search(
                            [("barcode", "=", item.get("empNo", 1))],
                            limit=1)  # Browse
                    elif employee_id_type == 'employee_id':
                        employee_id = self.env['hr.employee'].sudo().search(
                            [("id", "=", int(item.get("empNo", 1)))],
                            limit=1)  # Browse
                    else:
                        raise exceptions.UserError("Employee ID type not set in settings.")

                    if not employee_id or not employee_id.biometric_group_id:
                        continue
                    self.create({
                        "device_id": item.get("cpuid", ""),
                        "emp_no": item.get("empNo", ""),
                        "punch_time": item.get("punchTime", ""),
                        "name": employee_id.name,
                        "employee_id":employee_id.id,
                        "inout_mode": item.get("inOutMode", ""),
                    })
                # self.create(data_list)

        except Exception as e:
            raise exceptions.UserError(str(e))

    def _cron_sync_with_odoo(self):
        # Process in batches of 500 (oldest first) to avoid HTTP timeouts.
        # The cron runs automatically every 12 hours and chips away at the backlog.
        logs_without_synced = self.search([
            ("is_odoo_synced", '=', False),
        ], order="punch_time asc", limit=500)

        if not logs_without_synced:
            _logger.info("[BiometricSync] No unsynced logs found. Nothing to process.")
            return

        start_id = logs_without_synced[0].id
        end_id = logs_without_synced[-1].id
        total = len(logs_without_synced)
        _logger.info(
            "[BiometricSync] Starting batch sync — Start ID: %s | End ID: %s | Count: %s",
            start_id, end_id, total
        )

        # Group logs by employee
        grouped_logs = {}
        for log in logs_without_synced:
            employee_id = log.employee_id
            if employee_id.id not in grouped_logs:
                grouped_logs[employee_id.id] = []
            grouped_logs[employee_id.id].append(log)

        for employee_id, logs in grouped_logs.items():
            #smritimay
            if not employee_id:
                # Skip corrupted biometric logs (no mail.thread mixin, so just mark as synced)
                for log in logs:
                    log.write({'is_odoo_synced': True})
                continue
            #smritimay
            
            try:
                employee = self.env['hr.employee'].browse(employee_id)
                employee_tz = employee.tz or 'UTC'
                employee_tz = pytz.timezone(employee_tz)
                biometric_config = self.env['biometric.config'].search([], limit=1)

                # Sort logs by punch time
                logs_sorted = sorted(logs, key=lambda x: datetime.strptime(x.punch_time, "%Y-%m-%dT%H:%M:%S"))

                # Group logs by date
                today_logs = {}
                for log in logs_sorted:
                    punch_time = datetime.strptime(log.punch_time, "%Y-%m-%dT%H:%M:%S")
                    date = punch_time.date()
                    if date not in today_logs:
                        today_logs[date] = []
                    today_logs[date].append(log)

                # Process logs for each date
                for date, logs in today_logs.items():
                    check_in_utc = None
                    check_out_utc = None
                    check_in_log = None
                    check_out_log = None

                    # Handling mode 10 (Even-Odd)
                    if logs[0].inout_mode == '10':
                        if biometric_config.attendance_inout_type == "first_last":
                            check_in_log = logs[0]  # First log is check-in
                            check_out_log = None

                            existing_attendance = self.env['hr.attendance'].search([

                                ('employee_id', '=', employee_id),

                                ('check_in', '>=', date.strftime('%Y-%m-%d 00:00:00')),

                                ('check_in', '<=', date.strftime('%Y-%m-%d 23:59:59')),


                            ], limit=1)

                            if len(logs) == 1:
                                # Create a fake checkout log
                                fake_checkout_log = logs[0].copy()
                                # If no checkout log exists, set a default check-out time
                                if date < datetime.now().date():
                                    # Set checkout time to 8:30 AM on that date
                                    checkout_time_str = str(
                                        employee.resource_calendar_id.checkout_time_for_single_punch)  # e.g., '17.5'

                                    # Convert to float to separate hours and minutes
                                    checkout_time_float = float(checkout_time_str)
                                    hours = int(checkout_time_float)  # Get the whole number part for hours
                                    minutes = int((checkout_time_float - hours) * 60)

                                    checkout_time = datetime.combine(date, (datetime.min + timedelta(hours=int(employee.resource_calendar_id.checkout_time_for_single_punch), minutes=int((employee.resource_calendar_id.checkout_time_for_single_punch % 1) * 60))).time())

                                    punch_time_local_naive = checkout_time  # Use the fake checkout time
                                    punch_time_local = employee_tz.localize(punch_time_local_naive)
                                    check_out_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)
                                    fake_checkout_log.punch_time = checkout_time.isoformat()
                                    logs.append(fake_checkout_log)# Update the fake checkout log punch time

                            if len(logs) > 1:
                                check_out_log = logs[-1]  # Last log is check-out
                            if existing_attendance:
                                check_out_log = logs[-1]
                                check_in_log = None



                            if check_in_log and not existing_attendance:
                                punch_time_local_naive = datetime.strptime(check_in_log.punch_time, "%Y-%m-%dT%H:%M:%S")
                                punch_time_local = employee_tz.localize(punch_time_local_naive)
                                check_in_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)
                                att_vals = {
                                    'employee_id': employee_id,
                                    'check_in': check_in_utc,
                                    'in_mode': 'biometric_device',
                                    'in_biometric_device': self.env["biometric.device"].search(
                                        [("cpuid", "=", check_in_log.device_id)], limit=1).id or None,
                                }

                            if check_out_log and check_out_log != check_in_log:
                                punch_time_local_naive = datetime.strptime(check_out_log.punch_time,
                                                                           "%Y-%m-%dT%H:%M:%S")
                                punch_time_local = employee_tz.localize(punch_time_local_naive)
                                check_out_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)
                                if check_out_utc and existing_attendance:
                                    existing_attendance.write({
                                        'check_out': check_out_utc,
                                        'out_mode': 'biometric_device',
                                        'out_biometric_device': self.env["biometric.device"].search(
                                            [("cpuid", "=", check_out_log.device_id)], limit=1).id or None,
                                    })
                                    for log in logs:
                                        log.is_odoo_synced = True
                                    continue
                                else:
                                    att_vals.update({
                                        'check_out': check_out_utc,
                                        'out_mode': 'biometric_device',
                                        'out_biometric_device': self.env["biometric.device"].search(
                                            [("cpuid", "=", check_out_log.device_id)], limit=1).id or None,
                                    })
                            if att_vals.get('check_in') and att_vals.get('check_out'):
                                if att_vals.get('check_in') > att_vals.get('check_out') and att_vals.get('check_in').date() < datetime.now().date():
                                    att_vals["check_out"] = att_vals.get('check_in')
                                    att_vals["is_single_punch"] = True
                            self.env['hr.attendance'].create(att_vals)


                        elif biometric_config.attendance_inout_type == "odd_even":
                            # for idx in range(0, len(logs), 2):
                            #     check_in_log = logs[idx]
                            #     punch_time_local_naive = datetime.strptime(check_in_log.punch_time,"%Y-%m-%dT%H:%M:%S")
                            #     punch_time_local = employee_tz.localize(punch_time_local_naive)
                            #     check_in_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)

                            # Check for existing attendance records without a check-out
                            for idx in range(0, len(logs)):
                                if logs[idx].is_odoo_synced:
                                    continue
                                existing_attendance = self.env['hr.attendance'].search([

                                    ('employee_id', '=', employee_id),

                                    ('check_in', '>=', date.strftime('%Y-%m-%d 00:00:00')),

                                    ('check_in', '<=', date.strftime('%Y-%m-%d 23:59:59')),

                                    ('check_out', '=', False)

                                ], limit=1)

                                if existing_attendance:


                                    # Update existing record if there's a next log available

                                    # if idx + 1 < len(logs):
                                    #     check_out_log = logs[idx + 1]
                                    check_out_log = logs[idx]

                                    punch_time_local_naive = datetime.strptime(check_out_log.punch_time,
                                                                               "%Y-%m-%dT%H:%M:%S")

                                    punch_time_local = employee_tz.localize(punch_time_local_naive)

                                    check_out_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)

                                    existing_attendance.write({

                                        'check_out': check_out_utc,

                                        'out_mode': 'biometric_device',

                                        'out_biometric_device': self.env["biometric.device"].search(

                                            [("cpuid", "=", check_out_log.device_id)], limit=1).id or None,

                                    })
                                    logs[idx].write({"is_odoo_synced": True})

                                else:

                                    # No existing record found, create a new one
                                    check_in_log = logs[idx]
                                    punch_time_local_naive = datetime.strptime(check_in_log.punch_time,
                                                                               "%Y-%m-%dT%H:%M:%S")
                                    punch_time_local = employee_tz.localize(punch_time_local_naive)
                                    check_in_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)

                                    att_vals = {

                                        'employee_id': employee_id,

                                        'check_in': check_in_utc,

                                        'in_mode': 'biometric_device',

                                        'in_biometric_device': self.env["biometric.device"].search(

                                            [("cpuid", "=", check_in_log.device_id)], limit=1).id or None,

                                    }
                                    logs[idx].write({"is_odoo_synced": True})

                                    # If there's a check-out log available, add it
                                    for idxx in range(idx+1, len(logs)):

                                        if idxx < len(logs):
                                            check_out_log = logs[idxx]

                                            punch_time_local_naive = datetime.strptime(check_out_log.punch_time,
                                                                                       "%Y-%m-%dT%H:%M:%S")

                                            punch_time_local = employee_tz.localize(punch_time_local_naive)

                                            check_out_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)

                                            att_vals.update({

                                                'check_out': check_out_utc,

                                                'out_mode': 'biometric_device',

                                                'out_biometric_device': self.env["biometric.device"].search(

                                                    [("cpuid", "=", check_out_log.device_id)], limit=1).id or None,

                                            })
                                            logs[idxx].write({"is_odoo_synced": True})
                                            break

                                    # Create the new attendance record

                                    self.env['hr.attendance'].create(att_vals)

                    # Handling modes 11 (Check-In) and 12 (Check-Out)
                    elif logs[0].inout_mode in ['11', '12']:
                        check_in_logs = sorted([log for log in logs if log.inout_mode == '11'],
                                               key=lambda x: x.punch_time)
                        check_out_logs = sorted([log for log in logs if log.inout_mode == '12'],
                                                key=lambda x: x.punch_time)

                        # Check for existing attendance without checkout for today
                        existing_attendance = self.env['hr.attendance'].search([
                            ('employee_id', '=', employee_id),
                            ('check_in', '>=', date.strftime('%Y-%m-%d 00:00:00')),
                            ('check_in', '<=', date.strftime('%Y-%m-%d 23:59:59')),
                            ('check_out', '=', False)
                        ], limit=1)

                        if existing_attendance and check_out_logs:
                            # Update the existing record with the first check-out log
                            check_out_log = check_out_logs.pop(0)  # Get the first check-out log
                            punch_time_local_naive_checkout = datetime.strptime(check_out_log.punch_time,
                                                                                "%Y-%m-%dT%H:%M:%S")
                            punch_time_local_checkout = employee_tz.localize(punch_time_local_naive_checkout)
                            check_out_utc = punch_time_local_checkout.astimezone(pytz.utc).replace(tzinfo=None)

                            existing_attendance.write({
                                'check_out': check_out_utc,
                                'out_mode': 'biometric_device',
                                'out_biometric_device': self.env["biometric.device"].search(
                                    [("cpuid", "=", check_out_log.device_id)], limit=1).id or None,
                            })

                        # Iterate through remaining check-in logs
                        for check_in_log in check_in_logs:
                            # Process check-in
                            punch_time_local_naive = datetime.strptime(check_in_log.punch_time, "%Y-%m-%dT%H:%M:%S")
                            punch_time_local = employee_tz.localize(punch_time_local_naive)
                            check_in_utc = punch_time_local.astimezone(pytz.utc).replace(tzinfo=None)

                            # Prepare attendance values
                            att_vals = {
                                'employee_id': employee_id,
                                'check_in': check_in_utc,
                                'in_mode': 'biometric_device',
                                'in_biometric_device': self.env["biometric.device"].search(
                                    [("cpuid", "=", check_in_log.device_id)], limit=1).id or None,
                            }

                            # If there's at least one check-out log, get the next one
                            if check_out_logs:
                                check_out_log = check_out_logs.pop(0)  # Get the first check-out log
                                punch_time_local_naive_checkout = datetime.strptime(check_out_log.punch_time,
                                                                                    "%Y-%m-%dT%H:%M:%S")
                                punch_time_local_checkout = employee_tz.localize(punch_time_local_naive_checkout)
                                check_out_utc = punch_time_local_checkout.astimezone(pytz.utc).replace(tzinfo=None)

                                # Add check-out values to att_vals
                                att_vals.update({
                                    'check_out': check_out_utc,
                                    'out_mode': 'biometric_device',
                                    'out_biometric_device': self.env["biometric.device"].search(
                                        [("cpuid", "=", check_out_log.device_id)], limit=1).id or None,
                                })

                            # Create the new attendance record
                            self.env['hr.attendance'].create(att_vals)

                    for log in logs:
                        log.is_odoo_synced = True

            except Exception as e:
                _logger.error(
                    "[BiometricSync] Error syncing logs for employee ID %s: %s",
                    employee_id, str(e)
                )
                # Mark these logs as synced anyway so they don't block the queue forever.
                # Use a savepoint so this write commits even though the attendance creation failed.
                try:
                    for log in logs:
                        log.write({'is_odoo_synced': True})
                except Exception as mark_err:
                    _logger.error(
                        "[BiometricSync] Could not mark logs as synced for employee ID %s: %s",
                        employee_id, str(mark_err)
                    )


                """"
                try:
                    self.env['hr.attendance'].create(att_vals)
                except Exception as e:
                    record = self.env['hr.attendance'].search([
                        ('employee_id', '=', employee_id),
                        ('check_in', '=', check_in_utc),
                        ('check_out', '=', check_out_utc),
                    ])
                    if len(record) > 1:
                        record[-1].unlink()
                    continue
                """

# def _cron_sync_with_odoo_previous(self):
#     logs_without_synced = self.search([("is_odoo_synced", '=', True)])
#
#     grouped_logs = {}
#     for log in logs_without_synced:
#         employee_id = int(log.emp_no)
#         if employee_id not in grouped_logs:
#             grouped_logs[employee_id] = []
#         grouped_logs[employee_id].append(log)
#
#     for employee_id, logs in grouped_logs.items():
#         try:
#             # Fetch the employee record to get the timezone
#             employee = self.env['hr.employee'].browse(employee_id)
#             employee_tz = employee.tz or 'UTC'  # Default to 'UTC' if no timezone is set
#             employee_tz = pytz.timezone(employee_tz)
#
#             # Sort logs by punch_time to get the first and last
#             logs_sorted = sorted(logs, key=lambda x: datetime.strptime(x.punch_time, "%H:%M:%S").time())
#             first_log = logs_sorted[0]
#             last_log = logs_sorted[-1]
#
#             # Assuming you want the current date combined with punch times
#             today = fields.Date.today()
#             punch_time_format = "%H:%M:%S"
#
#             # Convert punch times to naive datetime in local time
#             check_in_local_naive = datetime.combine(today, datetime.strptime(first_log.punch_time, punch_time_format).time())
#             check_out_local_naive = datetime.combine(today, datetime.strptime(last_log.punch_time, punch_time_format).time())
#
#             # Ensure these times are in the employee's local timezone
#             check_in_local = employee_tz.localize(check_in_local_naive)
#             check_out_local = employee_tz.localize(check_out_local_naive)
#
#             # Convert the localized datetime to UTC
#             check_in_utc = check_in_local.astimezone(pytz.utc).replace(tzinfo=None)
#             check_out_utc = check_out_local.astimezone(pytz.utc).replace(tzinfo=None)
#
#             # Create or update the attendance record
#             try:
#                 att = self.env['hr.attendance'].create({
#                     'employee_id': employee_id,
#                     'check_in': check_in_utc,
#                     'check_out': check_out_utc,
#                     "in_mode":'biometric_device',
#                     "out_mode":'biometric_device',
#                     "in_biometric_device": self.env["biometric.device"].search([("cpuid","=", first_log.device_id)]).id or None,
#                     "out_biometric_device": self.env["biometric.device"].search([("cpuid","=", last_log.device_id)]).id or None
#                 })
#             except Exception as e:
#                 record = self.env['hr.attendance'].search([
#                     ('employee_id','=',employee_id),
#                     ('check_in','=', check_in_utc),
#                     ('check_out','=', check_out_utc),
#                 ])
#                 if len(record)>1:
#                     record[-1].unlink()
#                 continue
#
#             # Mark all logs for this employee as synced
#             for log in logs:
#                 log.is_odoo_synced = True
#
#         except Exception as e:
#             raise exceptions.UserError(f"Error syncing logs for employee {employee_id}: {str(e)}")
