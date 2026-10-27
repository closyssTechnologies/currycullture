from odoo import models, fields, api
from odoo.exceptions import UserError
from io import BytesIO
import base64
import xlsxwriter


class CreditManagementSheet(models.Model):
    _name = "credit.management.sheet"
    _description = "Credit Management Sheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # 1. Transaction Type
    transaction_type = fields.Selection(
        [('I', 'I'), ('N', 'N'), ('R', 'R')],
        string="Transaction Type",
        compute="_compute_transaction_type",
        store=True,
        tracking=True
    )

    # 2. Beneficiary Code (Fixed)
    beneficiary_code = fields.Char(
        string="Beneficiary Code",
        default="A0001",
        readonly=True
    )

    # 3. Beneficiary Account Number
    beneficiary_acc_no = fields.Char(
        string='Beneficiary Account Number',
        compute='_compute_vendor_details',
        store=True
    )

    # 4. Instrument Amount
    amount = fields.Float(string="Instrument Amount", required=True, tracking=True)

    # 5. Beneficiary Name
    beneficiary_name = fields.Char(
        string='Beneficiary Name',
        compute='_compute_vendor_details',
        store=True
    )

    # Address Fields
    drawee_location = fields.Char(string="Drawee Location")
    print_location = fields.Char(string="Print Location")
    bene_address_1 = fields.Char(string="Bene Address 1")
    bene_address_2 = fields.Char(string="Bene Address 2")
    bene_address_3 = fields.Char(string="Bene Address 3")
    bene_address_4 = fields.Char(string="Bene Address 4")
    bene_address_5 = fields.Char(string="Bene Address 5")

    instruction_reference_number = fields.Char(
        string="Instruction Reference Number",
        compute='_compute_vendor_details',
        store=True
    )

    customer_reference = fields.Char(
        string="Customer Reference Number",
        default="Vendor",
        readonly=True
    )

    # Payment Details
    payment_details_1 = fields.Char(string="Payment Details 1")
    payment_details_2 = fields.Char(string="Payment Details 2")
    payment_details_3 = fields.Char(string="Payment Details 3")
    payment_details_4 = fields.Char(string="Payment Details 4")
    payment_details_5 = fields.Char(string="Payment Details 5")
    payment_details_6 = fields.Char(string="Payment Details 6")
    payment_details_7 = fields.Char(string="Payment Details 7")

    cheque_number = fields.Char(string="Cheque Number")
    chq_trn_date = fields.Date(
        string="Chq / Trn Date",
        default=lambda self: fields.Date.context_today(self),
        readonly=True
    )
    micr_number = fields.Char(string="MICR Number")

    # Bank fields from Vendor
    beneficiary_ifsc = fields.Char(
        string="IFC Code",
        compute='_compute_vendor_details',
        store=True
    )
    bene_bank_name = fields.Char(
        string="Bene Bank Name",
        compute="_compute_vendor_details",
        store=True
    )
    bene_bank_branch_name = fields.Char(string="Bene Bank Branch Name")

    beneficiary_email = fields.Char(
        string="Beneficiary email id",
        compute='_compute_vendor_details',
        store=True
    )

    vendor_id = fields.Many2one(
        'res.partner',
        string="Vendor",
        domain="[('supplier_rank', '>', 0)]",
        tracking=True
    )

    company_bank = fields.Many2one(
        'res.partner.bank',
        string="Company Bank",
        domain="[('partner_id', '=', company_partner_id)]",
        required=True
    )

    company_partner_id = fields.Many2one(
        'res.partner',
        string="Company Partner",
        related='company_id.partner_id',
        store=True,
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company,
        required=True
    )

    remarks = fields.Char(string="Remarks")



    # ✅ Compute vendor details
    @api.depends('vendor_id')
    def _compute_vendor_details(self):
        """Compute beneficiary details from vendor."""
        for record in self:
            if not record.vendor_id:
                record.beneficiary_name = ''
                record.beneficiary_email = ''
                record.beneficiary_acc_no = ''
                record.instruction_reference_number = ''
                record.beneficiary_ifsc = ''
                record.bene_bank_name = ''
                continue

            vendor = record.vendor_id
            bank = self.env['res.partner.bank'].search(
                [('partner_id', '=', vendor.id)],
                limit=1
            )

            record.beneficiary_name = vendor.name or ''
            record.beneficiary_email = vendor.email or ''

            if bank:
                record.beneficiary_acc_no = bank.acc_number or ''
                record.instruction_reference_number = bank.acc_number or ''
                # In Odoo 17, bank_bic is the SWIFT/BIC code
                # For IFSC, you might need a custom field on res.partner.bank
                record.beneficiary_ifsc = bank.bank_bic or (bank.bank_id.bic if bank.bank_id else '')
                record.bene_bank_name = bank.bank_id.name if bank.bank_id else ''
            else:
                record.beneficiary_acc_no = ''
                record.instruction_reference_number = ''
                record.beneficiary_ifsc = ''
                record.bene_bank_name = ''

    # ✅ Compute Transaction Type Logic
    @api.depends('vendor_id', 'company_bank', 'amount')
    def _compute_transaction_type(self):
        """Determine transaction type based on bank and amount."""
        for rec in self:
            if not rec.vendor_id or not rec.company_bank:
                rec.transaction_type = False
                continue

            # Get vendor's bank
            vendor_bank_name = ''
            if rec.vendor_id.bank_ids:
                vendor_bank = rec.vendor_id.bank_ids[0]
                vendor_bank_name = vendor_bank.bank_id.name if vendor_bank.bank_id else ''

            # Get company bank name
            company_bank_name = rec.company_bank.bank_id.name if rec.company_bank.bank_id else ''

            # Determine transaction type
            if vendor_bank_name and vendor_bank_name == company_bank_name:
                rec.transaction_type = 'I'  # Internal (same bank)
            elif rec.amount < 200000:
                rec.transaction_type = 'N'  # NEFT (below 2 lakhs)
            else:
                rec.transaction_type = 'R'  # RTGS (2 lakhs and above)



    def action_export_to_excel(self):
        # Get selected records
        active_ids = self.env.context.get('active_ids', [])
        records = self.browse(active_ids) if active_ids else self.search([])

        if not records:
            raise UserError("No records to export!")

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Credit Management System")

        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#366092',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        # Normal data cell format
        normal_format = workbook.add_format({'border': 1})

        headers = [
            'Transaction Type', 'Beneficiary Code', 'Beneficiary Account Number',
            'Instrument Amount', 'Beneficiary Name', 'Drawee Location', 'Print Location',
            'Bene Address 1', 'Bene Address 2', 'Bene Address 3', 'Bene Address 4',
            'Bene Address 5', 'Instruction Reference Number', 'Customer Reference Number',
            'Payment Details 1', 'Payment Details 2', 'Payment Details 3',
            'Payment Details 4', 'Payment Details 5', 'Payment Details 6',
            'Payment Details 7', 'Cheque Number', 'Chq / Trn Date', 'MICR Number',
            'IFC Code', 'Bene Bank Name', 'Bank Branch Name', 'Beneficiary email id'
        ]

        # Write headers
        for col, title in enumerate(headers):
            worksheet.write(0, col, title, header_format)

        # Write data
        row = 1
        for rec in records:
            worksheet.write(row, 0, dict(rec._fields['transaction_type'].selection).get(rec.transaction_type, ''), normal_format)
            worksheet.write(row, 1, rec.beneficiary_code or '', normal_format)
            worksheet.write(row, 2, rec.beneficiary_acc_no or '', normal_format)
            worksheet.write(row, 3, rec.amount or 0, normal_format)
            worksheet.write(row, 4, rec.beneficiary_name or '', normal_format)
            worksheet.write(row, 5, rec.drawee_location or '', normal_format)
            worksheet.write(row, 6, rec.print_location or '', normal_format)
            worksheet.write(row, 7, rec.bene_address_1 or '', normal_format)
            worksheet.write(row, 8, rec.bene_address_2 or '', normal_format)
            worksheet.write(row, 9, rec.bene_address_3 or '', normal_format)
            worksheet.write(row, 10, rec.bene_address_4 or '', normal_format)
            worksheet.write(row, 11, rec.bene_address_5 or '', normal_format)
            worksheet.write(row, 12, rec.instruction_reference_number or '', normal_format)
            worksheet.write(row, 13, rec.customer_reference or '', normal_format)
            worksheet.write(row, 14, rec.payment_details_1 or '', normal_format)
            worksheet.write(row, 15, rec.payment_details_2 or '', normal_format)
            worksheet.write(row, 16, rec.payment_details_3 or '', normal_format)
            worksheet.write(row, 17, rec.payment_details_4 or '', normal_format)
            worksheet.write(row, 18, rec.payment_details_5 or '', normal_format)
            worksheet.write(row, 19, rec.payment_details_6 or '', normal_format)
            worksheet.write(row, 20, rec.payment_details_7 or '', normal_format)
            worksheet.write(row, 21, rec.cheque_number or '', normal_format)
            worksheet.write(row, 22, rec.chq_trn_date.strftime('%Y-%m-%d') if rec.chq_trn_date else '', normal_format)
            worksheet.write(row, 23, rec.micr_number or '', normal_format)
            worksheet.write(row, 24, rec.beneficiary_ifsc or '', normal_format)
            worksheet.write(row, 25, rec.bene_bank_name or '', normal_format)
            worksheet.write(row, 26, rec.bene_bank_branch_name or '', normal_format)
            worksheet.write(row, 27, rec.beneficiary_email or '', normal_format)
            row += 1

        # Auto adjust column width
        for i in range(len(headers)):
            worksheet.set_column(i, i, 26)

        # Optional: set column width
        """for i in range(28):
            worksheet.set_column(i, i, 26)"""

        workbook.close()

        # Create attachment
        output.seek(0)
        file_data = base64.b64encode(output.read())
        filename = f"{fields.Date.today()}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': file_data,
            'type': 'binary',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        # Return URL to download
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self'
        }