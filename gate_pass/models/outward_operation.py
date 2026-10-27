from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class OutwardGateEntry(models.Model):
    _name = 'outward.gate.entry'
    _description = 'Outward Gate Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'gate_entry_no desc'

    name = fields.Char(string='Gate Entry No', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))
    gate_entry_no = fields.Char(string='Gate Entry Number', required=True,
                                copy=False, readonly=True,
                                default=lambda self: _('New'))

    # Basic Information
    date = fields.Datetime(string='Date', default=fields.Datetime.now,
                           required=True, tracking=True)
    vehicle_no = fields.Char(string='Vehicle Number', required=True, tracking=True)
    driver_name = fields.Char(string='Driver Name', tracking=True)
    driver_phone = fields.Char(string='Driver Phone', tracking=True)

    # Sale Order Reference
    sale_order_id = fields.Many2one('sale.order', string='Sale Order',
                                    required=True, tracking=True,
                                    domain=[('state', 'in', ['sale', 'done'])])
    customer_id = fields.Many2one(related='sale_order_id.partner_id',
                                  string='Customer', store=True, readonly=True)

    # E-Way Bill and Tax Invoice
    eway_bill_no = fields.Char(string='E-Way Bill Number', tracking=True)
    eway_bill_date = fields.Date(string='E-Way Bill Date', tracking=True)
    tax_invoice_no = fields.Char(string='Tax Invoice Number', tracking=True,
                                help='Enter the tax invoice number for this outward entry')

    # Weight and Transport
    total_weight = fields.Float(string='Total Weight (Kg)', tracking=True)
    transport_company = fields.Char(string='Transport Company', tracking=True)

    # User Information
    gatekeeper_id = fields.Many2one('res.users', string='Gatekeeper',
                                    default=lambda self: self.env.user,
                                    required=True, tracking=True,
                                    domain="[('x_gate_entry_manager', '=', 'manager')]")

    # Product Lines
    outward_line_ids = fields.One2many('outward.gate.entry.line',
                                       'outward_gate_id',
                                       string='Outward Products')

    # Status and Notes
    state = fields.Selection([
        ('entry', 'Entry'),
        ('hold', 'Hold'),
        ('exit', 'Exit'),
    ], string='Status', default='entry', tracking=True)

    def action_entry(self):
        self.state = 'entry'

    def action_hold(self):
        self.state = 'hold'

    def action_exit(self):
        self.state = 'exit'

    def unlink(self):
        for record in self:
            if record.state == 'exit':
                raise ValidationError("You cannot delete a record in 'Exit' state.")
        return super(OutwardGateEntry, self).unlink()

    notes = fields.Text(string='Notes')

    # Computed Fields
    total_quantity = fields.Float(string='Total Quantity',
                                  compute='_compute_totals', store=True)
    product_count = fields.Integer(string='Product Count',
                                   compute='_compute_totals', store=True)

    @api.model
    def create(self, vals):
        if vals.get('gate_entry_no', _('New')) == _('New'):
            vals['gate_entry_no'] = self.env['ir.sequence'].next_by_code('outward.gate.entry') or _('New')
            vals['name'] = vals['gate_entry_no']
        return super(OutwardGateEntry, self).create(vals)

    def write(self, vals):
        for record in self:
            # Check if record is already in exit state
            if record.state == 'exit' and not self.env.context.get('bypass_exit_check'):
                # Analyze what is being changed
                if 'state' in vals:
                    continue
                
                # If state is NOT in vals, it means we are trying to edit a record that is ALREADY IN EXIT.
                raise ValidationError("You cannot edit this entry because it is in 'Exit' state.")

        return super(OutwardGateEntry, self).write(vals)

    @api.depends('outward_line_ids.gate_quantity')
    def _compute_totals(self):
        for record in self:
            record.total_quantity = sum(record.outward_line_ids.mapped('gate_quantity'))
            record.product_count = len(record.outward_line_ids)

    @api.onchange('sale_order_id')
    def _onchange_sale_order(self):
        """Auto-populate products from sale order with zero gate quantity"""
        if self.sale_order_id:
            lines = []
            for line in self.sale_order_id.order_line:
                if line.product_id.type in ['product', 'consu'] and line.product_uom_qty > 0:
                    # Calculate already delivered quantity
                    delivered_qty = sum(self.env['outward.gate.entry.line'].search([
                        ('sale_line_id', '=', line.id),
                        ('outward_gate_id.state', '=', 'exit')
                    ]).mapped('gate_quantity'))

                    remaining_qty = line.product_uom_qty - delivered_qty
                    if remaining_qty > 0:
                        lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom.id,
                            'ordered_quantity': line.product_uom_qty,  # This is the actual ordered quantity from SO
                            'gate_quantity': 0.0,  # Changed: Start with zero quantity - manual entry required
                            'sale_line_id': line.id,
                        }))
            self.outward_line_ids = lines

    @api.constrains('sale_order_id')
    def _check_duplicate_outward_gate_entry(self):
        """Prevent duplicate gate outward entries for same sale order"""
        for record in self:
            if record.sale_order_id:
                # Check if another gate entry exists for this sale order
                existing_entry = self.search([
                    ('sale_order_id', '=', record.sale_order_id.id),
                    ('id', '!=', record.id)
                ], limit=1)

                if existing_entry:
                    raise ValidationError(
                        f"A Gate Entry already exists for this Sale Order!\n"
                        f"Existing Gate Entry: {existing_entry.gate_entry_no}\n"
                        f"Sale Order: {record.sale_order_id.name}"
                    )

    def action_update_delivery_quantities(self):
        """Manual action to update delivery quantities"""
        self._update_delivery_quantities()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Delivery quantities have been updated successfully.'),
                'type': 'success',
            }
        }

    def _update_delivery_quantities(self):
        """Update delivery quantities when gate entry quantities are manually entered"""
        if self.sale_order_id:
            # Find related delivery picking
            delivery_pickings = self.env['stock.picking'].search([
                ('origin', '=', self.sale_order_id.name),
                ('picking_type_code', '=', 'outgoing'),
                ('state', 'not in', ['done', 'cancel'])
            ])

            for delivery_picking in delivery_pickings:
                # Create mapping of gate quantities
                gate_quantities = {}
                for gate_line in self.outward_line_ids:
                    if gate_line.gate_quantity > 0:
                        gate_quantities[gate_line.product_id.id] = gate_line.gate_quantity

                # DON'T update demand quantity - keep it as is
                # Only update the actual quantity (quantity field) which appears in the Quantity column
                for move_line in delivery_picking.move_line_ids_without_package:
                    if move_line.product_id.id in gate_quantities:
                        # Update the actual delivered quantity (this shows in Quantity column)
                        move_line.write({'quantity': gate_quantities[move_line.product_id.id]})
                    else:
                        # Set to 0 for products not in gate entry
                        move_line.write({'quantity': 0.0})

                # If no move lines exist, create them
                if not delivery_picking.move_line_ids_without_package:
                    for move in delivery_picking.move_ids_without_package:
                        if move.product_id.id in gate_quantities:
                            # Create move line with the gate quantity
                            self.env['stock.move.line'].create({
                                'move_id': move.id,
                                'product_id': move.product_id.id,
                                'product_uom_id': move.product_uom.id,
                                'quantity': gate_quantities[move.product_id.id],
                                'location_id': move.location_id.id,
                                'location_dest_id': move.location_dest_id.id,
                                'picking_id': delivery_picking.id,
                            })

                # Recompute picking state
                delivery_picking._compute_state()

    def _update_delivery_status(self):
        """Update delivery status in related sale order"""
        if self.sale_order_id:
            # Check if all products are delivered
            all_delivered = True
            for order_line in self.sale_order_id.order_line:
                if order_line.product_id.type in ['product', 'consu']:
                    delivered_qty = sum(self.env['outward.gate.entry.line'].search([
                        ('sale_line_id', '=', order_line.id),
                        ('outward_gate_id.state', '=', 'exit')
                    ]).mapped('gate_quantity'))

                    if delivered_qty < order_line.product_uom_qty:
                        all_delivered = False
                        break

            # Update sale order delivery status if needed
            if all_delivered and self.sale_order_id.state == 'sale':
                # You can add custom field to track delivery status
                self.sale_order_id.message_post(
                    body=_('All products have been dispatched through gate entry %s') % self.gate_entry_no
                )

    def name_get(self):
        """Display gate entry number in dropdowns"""
        result = []
        for record in self:
            name = record.gate_entry_no
            if record.state == 'draft':
                name = _('%s (Draft)') % name
            result.append((record.id, name))
        return result

    def action_print_outward_receipt(self):
        """Print outward receipt report"""
        return self.env.ref('gate_pass.action_report_outward_receipt_from_outward_operation').report_action(self)


class OutwardGateEntryLine(models.Model):
    _name = 'outward.gate.entry.line'
    _description = 'Outward Gate Entry Line'

    outward_gate_id = fields.Many2one('outward.gate.entry', string='Outward Gate Entry',
                                      ondelete='cascade', required=True)

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)

    # Quantities
    ordered_quantity = fields.Float(string='Ordered Qty', readonly=True, store=True)
    gate_quantity = fields.Float(string='Gate Outward Qty', required=True)

    # Sale Order Line Reference
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')

    # Additional Information
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number',
                             domain="[('product_id', '=', product_id)]")
    notes = fields.Text(string='Notes')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id

    @api.onchange('gate_quantity')
    def _onchange_gate_quantity(self):
        """Update delivery quantities when gate quantity is manually changed"""
        if self.outward_gate_id and self.outward_gate_id.sale_order_id:
            # Trigger delivery update when quantity is manually entered
            self.outward_gate_id._update_delivery_quantities()

    def write(self, vals):
        """Override write to update delivery quantities when gate_quantity changes"""
        result = super(OutwardGateEntryLine, self).write(vals)
        if 'gate_quantity' in vals:
            for record in self:
                if record.outward_gate_id and record.outward_gate_id.sale_order_id:
                    record.outward_gate_id._update_delivery_quantities()
        return result

    @api.constrains('gate_quantity', 'ordered_quantity')
    def _check_quantities(self):
        for line in self:
            if line.gate_quantity < 0:
                raise ValidationError(_('Gate quantity cannot be negative.'))
            # Only check against ordered quantity if there's a sale line reference
            if line.sale_line_id and line.gate_quantity > line.ordered_quantity:
                raise ValidationError(_('Gate quantity cannot exceed ordered quantity.'))

    @api.constrains('gate_quantity')
    def _check_available_quantity(self):
        """Check if the gate quantity doesn't exceed available quantity"""
        for line in self:
            if line.sale_line_id:
                # Calculate total delivered quantity for this sale line
                delivered_qty = sum(self.env['outward.gate.entry.line'].search([
                    ('sale_line_id', '=', line.sale_line_id.id),
                    ('outward_gate_id.state', '=', 'exit'),
                    ('id', '!=', line.id)
                ]).mapped('gate_quantity'))

                available_qty = line.sale_line_id.product_uom_qty - delivered_qty
                if line.gate_quantity > available_qty:
                    raise ValidationError(
                        _('Gate quantity (%s) exceeds available quantity (%s) for product %s.') %
                        (line.gate_quantity, available_qty, line.product_id.name)
                    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    outward_gate_ids = fields.One2many('outward.gate.entry', 'sale_order_id',
                                       string='Outward Gate Entries')
    outward_gate_count = fields.Integer(string='Gate Entry Count',
                                        compute='_compute_outward_gate_count')

    @api.depends('outward_gate_ids')
    def _compute_outward_gate_count(self):
        for order in self:
            order.outward_gate_count = len(order.outward_gate_ids)

    def action_view_outward_gates(self):
        """Action to view related outward gate entries"""
        action = self.env.ref('your_module.action_outward_gate_entry').read()[0]
        action['context'] = {
            'default_sale_order_id': self.id,
        }
        if len(self.outward_gate_ids) > 1:
            action['domain'] = [('id', 'in', self.outward_gate_ids.ids)]
        elif self.outward_gate_ids:
            action['views'] = [(self.env.ref('your_module.view_outward_gate_entry_form').id, 'form')]
            action['res_id'] = self.outward_gate_ids.id
        else:
            action['domain'] = [('id', 'in', [])]
        return action


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Fields for gate entry integration
    gate_inward_id = fields.Many2one(
        'inward.operation',
        string='Gate Inward No',
        help="Select the inward gate entry"
    )

    origin_po_id = fields.Many2one(
        'purchase.order',
        string='Origin PO',
        compute='_compute_origin_references',
        store=True
    )

    origin_sale_id = fields.Many2one(
        'sale.order',
        string='Origin Sale Order',
        compute='_compute_origin_references',
        store=True
    )

    outward_gate_entry_id = fields.Many2one(
        'outward.gate.entry',
        string='Select Outward Gate Entry',
        domain="[('sale_order_id', '=', origin_sale_id), ('state', 'in', ['hold', 'exit'])]",
        help="Select the outward gate entry to auto-populate quantities"
    )

    # NEW FIELD: Vehicle Number for outward operations
    outward_vehicle_no = fields.Char(
        string='Vehicle Number',
        related='outward_gate_entry_id.vehicle_no',
        readonly=True,
        store=True,
        help="Vehicle number from the selected outward gate entry"
    )

    @api.depends('origin', 'picking_type_code')
    def _compute_origin_references(self):
        """Compute the purchase/sale order from origin field"""
        for picking in self:
            picking.origin_po_id = False
            picking.origin_sale_id = False

            if picking.origin:
                if picking.picking_type_code == 'outgoing':
                    # Try to find sale order by name in origin field
                    so = self.env['sale.order'].search([('name', '=', picking.origin)], limit=1)
                    picking.origin_sale_id = so.id if so else False

                elif picking.picking_type_code == 'incoming':
                    # Try to find purchase order by name
                    po = self.env['purchase.order'].search([('name', '=', picking.origin)], limit=1)
                    picking.origin_po_id = po.id if po else False

    @api.onchange('outward_gate_entry_id')
    def _onchange_outward_gate_entry(self):
        """Auto-update quantities from selected outward gate entry"""
        if self.outward_gate_entry_id and self.picking_type_code == 'outgoing':
            # Create a mapping of products to gate quantities
            gate_quantities = {}
            for gate_line in self.outward_gate_entry_id.outward_line_ids:
                # Only use gate quantities that are greater than 0 (manually entered)
                if gate_line.gate_quantity > 0:
                    gate_quantities[gate_line.product_id.id] = gate_line.gate_quantity

            # Update move lines - keep demand same, update quantity field
            for move_line in self.move_line_ids_without_package:
                if move_line.product_id.id in gate_quantities:
                    # Update quantity field to match gate entry
                    move_line.quantity = gate_quantities[move_line.product_id.id]
                else:
                    # Set to 0 for products not in gate entry
                    move_line.quantity = 0.0

            # If no detailed operations exist yet, create them
            if not self.move_line_ids_without_package and self.state in ['assigned', 'partially_available']:
                for move in self.move_ids_without_package:
                    if move.product_id.id in gate_quantities:
                        # Create move line with gate quantity
                        move_line_vals = {
                            'move_id': move.id,
                            'product_id': move.product_id.id,
                            'product_uom_id': move.product_uom.id,
                            'quantity': gate_quantities[move.product_id.id],
                            'location_id': move.location_id.id,
                            'location_dest_id': move.location_dest_id.id,
                            'picking_id': self.id,
                        }
                        self.env['stock.move.line'].create(move_line_vals)

            # Show notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Quantities and Vehicle Number updated from Gate Entry: {self.outward_gate_entry_id.gate_entry_no}',
                    'type': 'success',
                }
            }

    def action_update_from_gate_entry(self):
        """Manual button to update quantities from selected gate entry"""
        if not self.outward_gate_entry_id:
            raise ValidationError(_('Please select an Outward Gate Entry first.'))

        # Trigger the onchange method manually
        self._onchange_outward_gate_entry()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _(
                    'Quantities and Vehicle Number have been updated from Gate Entry: %s') % self.outward_gate_entry_id.gate_entry_no,
                'type': 'success',
            }
        }