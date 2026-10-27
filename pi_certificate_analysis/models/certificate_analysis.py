from odoo import api, fields, models

class PiCertificateAnalysis(models.Model):
    _name = 'pi.certificate.analysis'
    _description = 'Certificate of Analysis'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Reference', readonly=True, required=True, copy=False, default='New', tracking=True)

    testing_date = fields.Date('Testing Date', tracking=True)
    fssai_license_no = fields.Char('FSSAI License No.')
    product_id = fields.Many2one('product.product', 'Product name', tracking=True)
    pack_size_qty = fields.Char('Pack Size/Quantity')
    city_name = fields.Char('City Name (Warehouse location)')
    buyer = fields.Char('Buyer', tracking=True)
    invoice_no = fields.Char('Invoice No.')
    batch_qty = fields.Char('Batch of Quantity')
    carton_net_wt = fields.Char("Carton's net wt.")
    production_qty = fields.Char('Production details (Quantity)kg')

    batch_no = fields.Char('Batch No.', tracking=True)
    date_mfg = fields.Date('Date of Manufacturing')
    date_expiry = fields.Date('Date of Expiry', tracking=True)
    date_batch_release = fields.Date('Date of Batch Release')
    no_of_pkt_per_carton = fields.Char('No of Pkt per carton')
    consigned_to = fields.Char('Consigned To')
    product_dispatch_temp = fields.Char('Product Dispatch Temperature')
    final_product_temp = fields.Char('Final Product temperature(\u00b0C)')

    physical_ids = fields.One2many(
        'pi.certificate.analysis.line', 'analysis_id',
        string='Physical Parameters',
        domain=[('param_type', '=', 'physical')],
        copy=True
    )
    micro_ids = fields.One2many(
        'pi.certificate.analysis.line', 'analysis_id',
        string='Microbiological Parameters',
        domain=[('param_type', '=', 'micro')],
        copy=True
    )
    chemical_ids = fields.One2many(
        'pi.certificate.analysis.line', 'analysis_id',
        string='Chemical Parameters',
        domain=[('param_type', '=', 'chemical')],
        copy=True
    )

    @api.model
    def create(self, vals):

        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pi.certificate.analysis') or 'New'
        return super().create(vals)

    def name_get(self):
        result = []
        for rec in self:
            name = "%s - %s" % (rec.name, rec.product_id.name if rec.product_id else 'Draft')
            result.append((rec.id, name))
        return result


class PiCertificateAnalysisLine(models.Model):
    _name = 'pi.certificate.analysis.line'
    _description = 'Certificate of Analysis Line'

    analysis_id = fields.Many2one('pi.certificate.analysis', string='Analysis', ondelete='cascade')
    param_type = fields.Selection([
        ('physical', 'Physical'),
        ('micro', 'Microbiological'),
        ('chemical', 'Chemical')
    ], string='Parameter Type', required=True)

    sr_no_physical = fields.Integer('Sr. No.', compute='_compute_sr_no_physical')
    sr_no_micro = fields.Integer('Sr. No.', compute='_compute_sr_no_micro')
    sr_no_chemical = fields.Integer('Sr. No.', compute='_compute_sr_no_chemical')

    name = fields.Char('Parameter')
    standard = fields.Char('Standard')
    test_report = fields.Char('Test Report')
    test_method = fields.Char('Test method')

    @api.depends('analysis_id.physical_ids')
    def _compute_sr_no_physical(self):
        for record in self:
            record.sr_no_physical = 0
            if record.analysis_id and record.param_type == 'physical':
                for i, line in enumerate(record.analysis_id.physical_ids):
                    if line == record:
                        record.sr_no_physical = i + 1
                        break

    @api.depends('analysis_id.micro_ids')
    def _compute_sr_no_micro(self):
        for record in self:
            record.sr_no_micro = 0
            if record.analysis_id and record.param_type == 'micro':
                for i, line in enumerate(record.analysis_id.micro_ids):
                    if line == record:
                        record.sr_no_micro = i + 1
                        break

    @api.depends('analysis_id.chemical_ids')
    def _compute_sr_no_chemical(self):
        for record in self:
            record.sr_no_chemical = 0
            if record.analysis_id and record.param_type == 'chemical':
                for i, line in enumerate(record.analysis_id.chemical_ids):
                    if line == record:
                        record.sr_no_chemical = i + 1
                        break




