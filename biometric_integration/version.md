
Version: 17.0.1.0
1.In device list only show assigned device —- done
2. When add device to company send device friendly name and timezone(New api added) –done
	Issue : Whatever time zone I sent it always take :+5:30 .Issue in Portal also
3.Device model name show (Subtype Shown) — done
4. Employee Inactive — Done
5. Employee Id or batch ID —-done
6. Log to Odoo attendance sync .If Employee not found skip —----done
7. Attendance punch time interval—- Done
8.Device status . —done
9. OU remove then Employee Inactive10.  Log employee name bug —done
11. 11_12 need first and last sync feature also
12. When fetch unassigned devices if any assigned device found assigned device … convert unassigned —------done

Version: 17.0.2.0
App name change

'version': 17.0.2.1,

1. biometric_configure_device_sync_time_interval selection field change to char

'version': '17.0.2.2'
[Update] 1. update code for bio_company missing


'version': '17.0.2.3',
[FIX] Logics bugs for attendance sync

'version': '17.0.2.4',

[UPDATE] Dummy data removed



 'version': '17.0.3.0',
 [UPDATE] biometric_integration: 1. Update single punch issue
            2. Added cron for set missing attendance
 19 Nov,2024
'version': '17.0.3.1',
[UPDATE] update code for sync where check if any attendance checkin is greater than checkout

20 Jan,2024
'version': '17.0.3.2',
[UPDATE] Except raise comment and post logs on bio config