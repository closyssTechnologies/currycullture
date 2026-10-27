from odoo import models, fields, api
from datetime import datetime
import calendar

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    meter_cost_line_ids = fields.One2many(
        'mrp.meter.cost.line',
        'production_id',
        store=True
    )

    labor_cost = fields.Float(
        string="Labor Cost",
        compute="_compute_labor_cost",
        readonly=True,
        store=False
    )

    total_cost = fields.Float(
        string="Total Cost",
        compute="_compute_total_cost",
        store=False
    )    

    electricity_cost = fields.Float(string="Electricity", compute="_compute_electricity_cost", store=False)
    gas_cost = fields.Float(string="Gas", compute="_compute_gas_costs", store=False)
    water_cost = fields.Float(string="Water", compute="_compute_water_costs", store=False)

    landed_cost = fields.Float(string="Landed Cost", compute="_compute_landed_cost", store=False)

    @api.depends('electricity_cost', 'gas_cost', 'water_cost')
    def _compute_landed_cost(self):
        for record in self:
            record.landed_cost = (record.electricity_cost or 0.0) + (record.gas_cost or 0.0) + (
                        record.water_cost or 0.0)

    @api.depends('date_finished', 'bom_id')
    def _compute_electricity_cost(self):
        MeterData = self.env['hms.meter.data']
        for record in self:
            record.electricity_cost = 0.0

            if not record.date_finished or not record.bom_id or not record.bom_id.bom_category_id:
                continue

            bom_category = record.bom_id.bom_category_id.name
            mo_date = record.date_finished.date()
            start = fields.Datetime.to_datetime(f"{mo_date} 00:00:00")
            end = fields.Datetime.to_datetime(f"{mo_date} 23:59:59")

            # Get electricity records for the day
            meter_records = MeterData.search([
                ('data_datetime', '>=', start),
                ('data_datetime', '<=', end),
                ('meter_type_id.name', '=', 'Electricity'),
            ])

            # Sum up actual cost: units * unit_costing
            total_elec_cost = sum(m.data * (m.meter_id.unit_costing or 0.0) for m in meter_records)
            total_pb_elec_cost = sum(100 * (m.meter_id.unit_costing or 0.0) for m in meter_records)
            total_sfb_elec_cost = sum(100 * (m.meter_id.unit_costing or 0.0) for m in meter_records)

            # Get all MOs on same date
            same_day_mos = self.env['mrp.production'].search([
                ('date_finished', '>=', start),
                ('date_finished', '<=', end),
                ('state', '=', 'done'),
            ])

            sfb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "SFB (Work-In-Progress)")
            pb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "PB (Packaging BOM)")
            mb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "MB (Manufacturing BOM)")

            sfb_count = len(sfb_mos)
            pb_count = len(pb_mos)
            mb_count = len(mb_mos)

            if sfb_count == 0 and pb_count == 0:
                # All cost goes to MB
                if bom_category == "MB (Manufacturing BOM)" and mb_count > 0:
                    record.electricity_cost = total_elec_cost / mb_count if total_elec_cost > 0 else 0.0

            elif sfb_count == 0 and pb_count > 0:
                if bom_category == "PB (Packaging BOM)":
                    record.electricity_cost = total_pb_elec_cost / pb_count
                elif bom_category == "MB (Manufacturing BOM)" and mb_count > 0:
                    remaining_cost = total_elec_cost - total_pb_elec_cost
                    record.electricity_cost = remaining_cost / mb_count if remaining_cost > 0 else 0.0

            elif pb_count == 0 and sfb_count > 0:
                if bom_category == "SFB (Work-In-Progress)":
                    record.electricity_cost = total_sfb_elec_cost / sfb_count
                elif bom_category == "MB (Manufacturing BOM)" and mb_count > 0:
                    remaining_cost = total_elec_cost - total_sfb_elec_cost
                    record.electricity_cost = remaining_cost / mb_count if remaining_cost > 0 else 0.0

            else:
                if bom_category == "SFB (Work-In-Progress)":
                    record.electricity_cost = total_sfb_elec_cost / sfb_count
                elif bom_category == "PB (Packaging BOM)":
                    record.electricity_cost = total_pb_elec_cost / pb_count
                elif bom_category == "MB (Manufacturing BOM)" and mb_count > 0:
                    remaining_cost = total_elec_cost - total_sfb_elec_cost - total_pb_elec_cost
                    record.electricity_cost = remaining_cost / mb_count if remaining_cost > 0 else 0.0

    @api.depends('date_finished', 'bom_id')
    def _compute_gas_costs(self):
        MeterData = self.env['hms.meter.data']
        for record in self:
            record.gas_cost = 0.0

            if not record.date_finished or not record.bom_id or not record.bom_id.bom_category_id:
                continue

            bom_category = record.bom_id.bom_category_id.name
            mo_date = record.date_finished.date()
            start = fields.Datetime.to_datetime(f"{mo_date} 00:00:00")
            end = fields.Datetime.to_datetime(f"{mo_date} 23:59:59")

            # Get electricity records for the day
            meter_records = MeterData.search([
                ('data_datetime', '>=', start),
                ('data_datetime', '<=', end),
                ('meter_type_id.name', '=', 'Gas'),
            ])

            # Sum up actual cost: units * unit_costing
            total_gas_cost = sum(m.data * (m.meter_id.unit_costing or 0.0) for m in meter_records)

            # Get all MOs on same date
            same_day_mos = self.env['mrp.production'].search([
                ('date_finished', '>=', start),
                ('date_finished', '<=', end),
                ('state', '=', 'done'),
            ])

            sfb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "SFB (Work-In-Progress)")
            pb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "PB (Packaging BOM)")
            mb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "MB (Manufacturing BOM)")

            sfb_count = len(sfb_mos)
            pb_count = len(pb_mos)
            mb_count = len(mb_mos)

            if bom_category == "SFB (Work-In-Progress)":
                record.gas_cost = 0.0
            elif bom_category == "PB (Packaging BOM)":
                record.gas_cost = 0.0
            elif bom_category == "MB (Manufacturing BOM)" and mb_count > 0:
                remaining_cost = total_gas_cost
                record.gas_cost = remaining_cost / mb_count if remaining_cost > 0 else 0.0

    @api.depends('date_finished', 'bom_id')
    def _compute_water_costs(self):
        MeterData = self.env['hms.meter.data']
        for record in self:
            record.water_cost = 0.0

            if not record.date_finished or not record.bom_id or not record.bom_id.bom_category_id:
                continue

            bom_category = record.bom_id.bom_category_id.name
            mo_date = record.date_finished.date()
            start = fields.Datetime.to_datetime(f"{mo_date} 00:00:00")
            end = fields.Datetime.to_datetime(f"{mo_date} 23:59:59")

            # Get electricity records for the day
            meter_records = MeterData.search([
                ('data_datetime', '>=', start),
                ('data_datetime', '<=', end),
                ('meter_type_id.name', '=', 'Water'),
            ])

            # Sum up actual cost: units * unit_costing
            total_water_cost = sum(m.data * (m.meter_id.unit_costing or 0.0) for m in meter_records)

            # Get all MOs on same date
            same_day_mos = self.env['mrp.production'].search([
                ('date_finished', '>=', start),
                ('date_finished', '<=', end),
                ('state', '=', 'done'),
            ])

            sfb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "SFB (Work-In-Progress)")
            pb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "PB (Packaging BOM)")
            mb_mos = same_day_mos.filtered(lambda mo: mo.bom_id.bom_category_id.name == "MB (Manufacturing BOM)")

            sfb_count = len(sfb_mos)
            pb_count = len(pb_mos)
            mb_count = len(mb_mos)

            if bom_category == "SFB (Work-In-Progress)":
                record.water_cost = 0.0
            elif bom_category == "PB (Packaging BOM)":
                record.water_cost = 0.0
            elif bom_category == "MB (Manufacturing BOM)" and mb_count > 0:
                remaining_cost = total_water_cost
                record.water_cost = remaining_cost / mb_count if remaining_cost > 0 else 0.0

    def action_allocate_meter_costs(self):
        for record in self:
            # record._compute_meter_costs()
            record._compute_labor_cost()
            record._compute_total_cost()

    @api.depends('date_finished')
    def _compute_meter_costs(self):
        Meter = self.env['hms.meter']
        MeterType = self.env['hms.meter.type']
        for record in self:
            record.meter_cost_line_ids = False

            if not record.date_finished or not record.bom_id or not record.bom_id.bom_category_id:
                continue

            scheduled_date = record.date_finished.date()

            same_day_orders = self.search([
                ('date_finished', '>=', fields.Datetime.to_datetime(f"{scheduled_date} 00:00:00")),
                ('date_finished', '<=', fields.Datetime.to_datetime(f"{scheduled_date} 23:59:59")),
                '|',
                ('bom_id.bom_category_id.name', '=', "SFB (Work-In-Progress)"),
                ('bom_id.bom_category_id.name', '=', "PB (Packaging BOM)")
            ])

            for meter_type in MeterType.search([]):
                meter = Meter.search([('meter_type_id', '=', meter_type.id)], limit=1)
                if not meter:
                    continue

                reading_line = next((
                    line for line in meter.meter_data_ids
                    if line.data_datetime.date() == scheduled_date
                ), None)

                if reading_line:
                    total_cost = reading_line.data
                    cost_per_mo = total_cost / len(same_day_orders) if same_day_orders else 0.0

                    self.env['mrp.meter.cost.line'].create({
                        'production_id': record.id or record._origin.id,
                        'meter_type_id': meter_type.id,
                        'allocated_cost': cost_per_mo
                    })

    @api.depends('date_finished', 'workorder_ids')
    def _compute_labor_cost(self):
        for record in self:
            record.labor_cost = record._calculate_labor_cost()

    def _calculate_labor_cost(self):
        labor_total = 0.0
        if not self.date_finished or not self.workorder_ids:
            return 0.0

        mo_date = self.date_finished.date()
        start_datetime = datetime.combine(mo_date, datetime.min.time())
        end_datetime = datetime.combine(mo_date, datetime.max.time())

        workcenter_ids = self.workorder_ids.mapped('workcenter_id')
        employee_ids = workcenter_ids.mapped('employee_ids')

        if not employee_ids:
            return 0.0

        present_attendances = self.env['hr.attendance'].search([
            ('employee_id', 'in', employee_ids.ids),
            ('check_in', '>=', start_datetime),
            ('check_in', '<=', end_datetime),
        ])

        present_employee_ids = present_attendances.mapped('employee_id')

        present_work_entries = self.env['hr.work.entry'].search([
            ('employee_id', 'in', employee_ids.ids),
            ('state', '=', 'validated'),
            ('work_entry_type_id.name', '=', 'Paid Time Off'),
            ('date_start', '>=', start_datetime),
            ('date_start', '<=', end_datetime),
            ('date_stop', '>=', start_datetime),
            ('date_stop', '<=', end_datetime),
        ])
        present_work_entry_employees = present_work_entries.mapped('employee_id')

        paid_time_off_leaves = self.env['hr.leave'].search([
            ('employee_id', 'in', employee_ids.ids),
            ('state', '=', 'validated'),
            ('holiday_status_id.name', '=', 'Paid Time Off'),
            ('date_from', '>=', start_datetime),
            ('date_from', '<=', end_datetime),
            ('date_to', '>=', start_datetime),
            ('date_to', '<=', end_datetime),
        ])
        paid_leave_employee_ids = paid_time_off_leaves.mapped('employee_id')

        considered_employee_ids = (present_employee_ids | paid_leave_employee_ids | present_work_entry_employees).ids

        year = mo_date.year
        month = mo_date.month
        _, days_in_month = calendar.monthrange(year, month)

        for emp in employee_ids:
            contract = self.env['hr.contract'].sudo().search([
                ('employee_id', '=', emp.id),
                ('state', '=', 'open'),
            ], limit=1)

            # if emp in present_employee_ids and contract:
            if emp.id in considered_employee_ids and contract:
                cal_wage = contract.per_day_wage or 0.0
                daily_wage = cal_wage / days_in_month

                emp_workcenters = self.env['mrp.workcenter'].search([
                    ('employee_ids', 'in', [emp.id])
                ])

                all_mos_same_day = self.env['mrp.production'].search([
                    ('workorder_ids.workcenter_id', 'in', emp_workcenters.ids),
                    ('date_finished', '>=', fields.Datetime.to_datetime(f"{mo_date} 00:00:00")),
                    ('date_finished', '<=', fields.Datetime.to_datetime(f"{mo_date} 23:59:59")),
                    ('state', '=', 'done'),
                ])

                mo_count = len(all_mos_same_day) or 1
                shared_wage = daily_wage / mo_count
                labor_total += shared_wage

        return labor_total

    # @api.model ....
    # def read(self, fields=None, load='_classic_read'):
    #     # Force compute labor cost on every read
    #     self._compute_labor_cost()
    #     return super().read(fields, load)

    @api.depends('meter_cost_line_ids.allocated_cost', 'labor_cost', 'landed_cost')
    def _compute_total_cost(self):
        for record in self:
            meter_total = sum(record.meter_cost_line_ids.mapped('allocated_cost'))
            # record.total_cost = meter_total + (record.labor_cost or 0.0) + (record.landed_cost or 0.0)
            record.total_cost = (record.labor_cost or 0.0) + (record.landed_cost or 0.0)
