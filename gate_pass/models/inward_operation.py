from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    gate_inward_id = fields.Many2one('inward.operation', string='Gate Inward No',
                                     domain="[('purchase_order_id', '=', origin_po_id)]")
    origin_po_id = fields.Many2one('purchase.order', string='Origin PO',
                                   compute='_compute_origin_po', store=True)

    # New fields for gate inward information
    gate_vehicle_no = fields.Char('Vehicle No', related='gate_inward_id.vehicle_no', readonly=True)
    gate_vendor_invoice_no = fields.Char('Vendor Invoice No', related='gate_inward_id.vendor_invoice_no', readonly=True)
    gate_invoice_date = fields.Date('Vendor Invoice Date', related='gate_inward_id.invoice_date', readonly=True)
    # Gate received date field that will be automatically populated
    gate_received_date = fields.Datetime('Receive Date & Time',
                                       help="Date and time when materials were received at gate. Auto-populated from Gate Inward.")
    # Vehicle number field that will be automatically populated
    vehicle_no = fields.Char('Vehicle Number', help="Vehicle number from Gate Inward. Auto-populated when Gate Inward is selected.")
    # ADDED: Gate pass number field
    gate_pass_no = fields.Char('Gate Pass No', help="Gate pass number from Gate Inward. Auto-populated when Gate Inward is selected.")
    # Owner field (will be auto-assigned from gate inward gatekeeper)
    owner_id = fields.Many2one('res.users', string='Assign Owner', readonly=True, help="Owner automatically assigned from Gate Inward gatekeeper.")

    @api.depends('origin')
    def _compute_origin_po(self):
        for picking in self:
            if picking.origin:
                po = self.env['purchase.order'].search([('name', '=', picking.origin)], limit=1)
                picking.origin_po_id = po.id if po else False
            else:
                picking.origin_po_id = False

    @api.onchange('gate_inward_id')
    def _onchange_gate_inward_id(self):
        """Auto-populate gate pass number, receive date & time, vehicle number, and owner from gate entry"""
        if self.gate_inward_id:
            self.gate_pass_no = self.gate_inward_id.name
            # Auto-populate receive date & time from gate inward
            self.gate_received_date = self.gate_inward_id.receiving_date
            # Auto-populate vehicle number from gate inward
            self.vehicle_no = self.gate_inward_id.vehicle_no
            # Auto-assign owner from gate inward gatekeeper
            if self.gate_inward_id.gatekeeper_user_id:
                self.owner_id = self.gate_inward_id.gatekeeper_user_id.id
            
            # Sync quantities from gate inward
            for move in self.move_ids_without_package:
                # Find matching inward line
                inward_line = self.gate_inward_id.product_line_ids.filtered(
                    lambda x: x.product_id == move.product_id
                )
                if inward_line:
                    # Update quantity on the move line (quantity field)
                    move.quantity = inward_line[0].receiving_qty
        else:
            # Clear all fields if no gate entry selected
            self.gate_pass_no = False
            # Clear receive date & time
            self.gate_received_date = False
            # Clear vehicle number
            self.vehicle_no = False
            # Clear owner
            self.owner_id = False

    def write(self, vals):
        result = super(StockPicking, self).write(vals)

        # Update receive date and vehicle number if gate_inward_id changes
        if 'gate_inward_id' in vals:
            for picking in self:
                if picking.gate_inward_id:
                    if picking.gate_inward_id.receiving_date:
                        picking.gate_received_date = picking.gate_inward_id.receiving_date
                    if picking.gate_inward_id.vehicle_no:
                        picking.vehicle_no = picking.gate_inward_id.vehicle_no
                    # ADDED: Update gate pass number
                    if picking.gate_inward_id.name:
                        picking.gate_pass_no = picking.gate_inward_id.name
                    # ADDED: Auto-assign owner from gatekeeper
                    if picking.gate_inward_id.gatekeeper_user_id:
                        picking.owner_id = picking.gate_inward_id.gatekeeper_user_id.id
                else:
                    picking.gate_received_date = False
                    picking.vehicle_no = False
                    picking.gate_pass_no = False
                    picking.owner_id = False

        # Commented out to avoid lot/serial number issues
        # When gate_inward_id is changed, update quantities immediately
        # if 'gate_inward_id' in vals:
        #     for picking in self:
        #         picking.sync_quantities_with_gate_entry()

        return result

    def sync_quantities_with_gate_entry(self):
        """Manually sync quantities with gate entry"""
        if self.gate_inward_id and self.state not in ['done', 'cancel']:
            for move in self.move_ids_without_package:
                # Find matching inward line
                inward_line = self.gate_inward_id.product_line_ids.filtered(
                    lambda x: x.product_id == move.product_id
                )

                if inward_line:
                    new_qty = inward_line[0].receiving_qty

                    # Only update move lines if they already exist
                    if move.move_line_ids:
                        for ml in move.move_line_ids:
                            ml.sudo().write({'quantity': new_qty})
                    else:
                        # Don't create new move lines automatically - let user do it manually
                        # Just update the stock.move quantity for reference
                        pass


# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     @api.onchange('quantity')
#     def _onchange_quantity(self):
#         """Auto-correct quantity to demand if exceeded"""
#         if self.quantity and self.product_uom_qty and self.quantity > self.product_uom_qty:
#             # Actually correct the quantity value
#             self.quantity = self.product_uom_qty
#             return {
#                 'warning': {
#                     'title': 'Quantity Adjusted!',
#                     'message': f'You entered more than demand ({self.product_uom_qty}). Quantity has been automatically set to maximum allowed ({self.product_uom_qty}).'
#                 }
#             }
#
#     @api.constrains('quantity', 'product_uom_qty')
#     def _check_quantity_limit(self):
#         """Additional safety check to prevent saving invalid quantities"""
#         for record in self:
#             if record.quantity and record.product_uom_qty and record.quantity > record.product_uom_qty:
#                 raise ValidationError(
#                     f'Quantity ({record.quantity}) cannot exceed demand ({record.product_uom_qty}) for product {record.product_id.name or "Unknown"}.'
#                 )


class InwardOperation(models.Model):
    _name = 'inward.operation'
    _description = 'Inward Operation'
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char('Gate Entry No', required=True, copy=False, readonly=True, default='New')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    vendor_invoice_no = fields.Char('Vendor Invoice No')
    vehicle_no = fields.Char('Vehicle No')
    driver_name = fields.Char('Driver Name')
    driver_mobile_no = fields.Char('Driver Mobile No')
    # READONLY: Vendor field is readonly and automatically set from purchase order
    vendor_id = fields.Many2one('res.partner', string='Vendor', readonly=True)
    eway_bill = fields.Char('E- Way Bill')
    invoice_date = fields.Date('Vendor Invoice Date')
    # Modified: Gatekeeper will be set when purchase order is selected
    gatekeeper_user_id = fields.Many2one('res.users', string='Gatekeeper/ User',
                                         domain="[('x_gate_entry_manager', '=', 'manager')]")
    # CHANGED: From Date to Datetime field
    receiving_date = fields.Datetime('Receiving Date & Time')  # Changed to Datetime
    weight = fields.Float('Weight')
    # Add state field to track record state
    state = fields.Selection([
        ('entry', 'Entry'),
        ('hold', 'Hold'),
        ('exit', 'Exit'),
    ], string='State', default='entry', tracking=True)

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
        return super(InwardOperation, self).unlink()


    product_line_ids = fields.One2many('inward.operation.line', 'inward_id', string='Product Lines')
    is_saved = fields.Boolean('Is Saved', compute='_compute_is_saved', store=False)

    @api.depends('create_date')
    def _compute_is_saved(self):
        """Check if record is saved (has create_date)"""
        for record in self:
            record.is_saved = bool(record.create_date)

    @api.model
    def _get_default_gatekeeper(self):
        """Get the first available gate entry manager as default gatekeeper"""
        manager = self.env['res.users'].search([
            ('x_gate_entry_manager', '=', 'manager'),
            ('active', '=', True)
        ], limit=1)
        return manager.id if manager else False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('inward.operation')
            if not sequence:
                current_date = fields.Date.today()
                vals['name'] = 'GI/%s/%s/0001' % (current_date.year, str(current_date.month).zfill(2))
            else:
                vals['name'] = sequence

        return super(InwardOperation, self).create(vals)

    @api.onchange('purchase_order_id')
    def _onchange_purchase_order(self):
        if self.purchase_order_id:
            self.vendor_id = self.purchase_order_id.partner_id.id
            # Auto-set gatekeeper when purchase order is selected
            self.gatekeeper_user_id = self._get_default_gatekeeper()
            # CHANGED: Auto-set receiving date and time to current datetime
            self.receiving_date = fields.Datetime.now()  # Changed to Datetime.now()

            # Clear existing lines first
            self.product_line_ids = [(5, 0, 0)]

            # Create new lines from purchase order
            lines = []
            for po_line in self.purchase_order_id.order_line:
                if po_line.product_id and po_line.product_qty > 0:  # Only add lines with products and quantities
                    line_vals = {
                        'product_id': po_line.product_id.id,
                        'ordered_qty': po_line.product_qty,
                        'receiving_qty': po_line.product_qty,  # Default receiving qty = ordered qty
                        'bill_quantity': po_line.product_qty,
                        'uom_id': po_line.product_uom.id if po_line.product_uom else po_line.product_id.uom_id.id,
                    }
                    lines.append((0, 0, line_vals))

            if lines:
                self.product_line_ids = lines
        else:
            self.vendor_id = False
            self.gatekeeper_user_id = False  # Clear gatekeeper when PO is cleared
            self.receiving_date = False  # Clear receiving date when PO is cleared
            self.product_line_ids = [(5, 0, 0)]

    def write(self, vals):
        # FIXED: Always ensure vendor_id is set from purchase_order_id to prevent it from disappearing
        # FIXED: Always ensure vendor_id is set from purchase_order_id to prevent it from disappearing
        for record in self:
            # Check if record is already in exit state
            if record.state == 'exit' and not self.env.context.get('bypass_exit_check'):
                # Analyze what is being changed
                # If we are changing state, it's allowed (e.g. if we add a 'Revert' button later, or system updates)
                if 'state' in vals:
                    # If other fields are also being changed, we should block if they are important?
                    # But usually Odoo writes everything at once.
                    # Ideally, if state is in vals, we assume it's a valid transition or update.
                    continue
                
                # If state is NOT in vals, it means we are trying to edit a record that is ALREADY IN EXIT.
                raise ValidationError("You cannot edit this entry because it is in 'Exit' state.")

        result = super(InwardOperation, self).write(vals)

        return result

    def update_related_pickings(self):
        """Update all pickings that reference this gate entry"""
        pickings = self.env['stock.picking'].search([
            ('gate_inward_id', '=', self.id),
            ('state', 'not in', ['done', 'cancel'])
        ])

        for picking in pickings:
            picking.sync_quantities_with_gate_entry()

    @api.constrains('purchase_order_id', 'vendor_invoice_no')
    def _check_duplicate_inward_gate_entry(self):
        """Prevent duplicate inward gate entries for same purchase order and vendor invoice"""
        for record in self:
            if record.purchase_order_id and record.vendor_invoice_no:
                # Check if another inward operation exists for this PO and vendor invoice
                existing_entry = self.search([
                    ('purchase_order_id', '=', record.purchase_order_id.id),
                    ('vendor_invoice_no', '=', record.vendor_invoice_no),
                    ('id', '!=', record.id)
                ], limit=1)

                if existing_entry:
                    raise ValidationError(
                        f"An Inward Gate Entry already exists for this combination!\n"
                        f"Existing Gate Entry: {existing_entry.name}\n"
                        f"Purchase Order: {record.purchase_order_id.name}\n"
                        f"Vendor Invoice No: {record.vendor_invoice_no}"
                    )

    @api.constrains('purchase_order_id')
    def _check_purchase_order_status(self):
        """Ensure purchase order is confirmed before creating inward gate entry"""
        for record in self:
            if record.purchase_order_id and record.purchase_order_id.state not in ['purchase', 'done']:
                raise ValidationError(
                    f"Cannot create Inward Gate Entry for Purchase Order {record.purchase_order_id.name}.\n"
                    f"Purchase Order must be confirmed first."
                )

    @api.constrains('gatekeeper_user_id')
    def _check_gatekeeper_admin(self):
        """Ensure only assigned gate entry managers can be selected as gatekeeper"""
        for record in self:
            if record.gatekeeper_user_id:
                if not hasattr(record.gatekeeper_user_id,
                               'x_gate_entry_manager') or record.gatekeeper_user_id.x_gate_entry_manager != 'manager':
                    raise ValidationError(
                        f"Only users assigned as Gate Entry Manager can be selected as Gatekeeper/User.\n"
                        f"Selected user '{record.gatekeeper_user_id.name}' is not assigned as a manager."
                    )
            else:
                # Auto-assign gatekeeper if none is set
                default_gatekeeper = self._get_default_gatekeeper()
                if default_gatekeeper:
                    record.gatekeeper_user_id = default_gatekeeper

    # ADDED: Method to ensure vendor is always set from purchase order
    @api.constrains('purchase_order_id')
    def _ensure_vendor_from_po(self):
        """Ensure vendor is always set from purchase order"""
        for record in self:
            if record.purchase_order_id:
                # Use sudo() to bypass readonly restriction for programmatic updates
                record.sudo().write({'vendor_id': record.purchase_order_id.partner_id.id})


class InwardOperationLine(models.Model):
    _name = 'inward.operation.line'
    _description = 'Inward Operation Line'

    inward_id = fields.Many2one('inward.operation', string='Inward Operation', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    ordered_qty = fields.Float('Ordered Qty', default=0.0)
    receiving_qty = fields.Float('Receiving Qty', default=0.0)
    balance_qty = fields.Float('Balance Qty', compute='_compute_balance_qty', store=True)
    bill_quantity = fields.Float('Bill Quantity', default=0.0)
    uom_id = fields.Many2one('uom.uom', string='UOM')

    @api.depends('ordered_qty', 'receiving_qty')
    def _compute_balance_qty(self):
        for line in self:
            line.balance_qty = line.ordered_qty - line.receiving_qty

    def write(self, vals):
        result = super(InwardOperationLine, self).write(vals)

        # If receiving_qty is changed, update related pickings
        if 'receiving_qty' in vals:
            for line in self:
                if line.inward_id:
                    line.inward_id.update_related_pickings()

        return result

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.uom_id:
            self.uom_id = self.product_id.uom_id.id
            self.receiving_qty = 0.0

    @api.constrains('receiving_qty', 'ordered_qty')
    def _check_receiving_qty(self):
        """Validate receiving quantity"""
        for line in self:
            # Skip validation if product is missing (garbage/ghost line)
            if not line.product_id:
                continue

            if line.receiving_qty < 0:
                raise ValidationError("Receiving quantity cannot be negative.")

            if line.receiving_qty > line.ordered_qty:
                raise ValidationError(
                    f"Receiving quantity ({line.receiving_qty}) cannot exceed ordered quantity ({line.ordered_qty}) "
                    f"for product {line.product_id.name}."
                )