from odoo import models, api, _
from odoo.exceptions import AccessError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def unlink(self):
        """Block deletion of confirmed orders - even for Gate Pass Managers"""
        for order in self:
            if order.state in ['sale', 'done']:
                # Check if user is admin/superuser OR has Administration access
                if not (self.env.user._is_superuser() or self.env.user.has_group('base.group_system') or self.env.user._is_admin()):
                    raise AccessError(_('Access Denied: Only System Administrator can delete confirmed Sale Orders.'))
        return super(SaleOrder, self).unlink()


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def unlink(self):
        """Block deletion of confirmed orders - even for Gate Pass Managers"""
        for order in self:
            if order.state in ['purchase', 'done']:
                # Check if user is admin/superuser OR has Administration access
                if not (self.env.user._is_superuser() or self.env.user.has_group('base.group_system') or self.env.user._is_admin()):
                    raise AccessError(_('Access Denied: Only System Administrator can delete confirmed Purchase Orders.'))
        return super(PurchaseOrder, self).unlink()


class InwardOperation(models.Model):
    _inherit = 'inward.operation'

    def unlink(self):
        """Block deletion of inward operations linked to confirmed purchase orders"""
        for record in self:
            if record.purchase_order_id and record.purchase_order_id.state in ['purchase', 'done']:
                # Check if user is admin/superuser OR has Administration access
                if not (self.env.user._is_superuser() or self.env.user.has_group('base.group_system') or self.env.user._is_admin()):
                    raise AccessError(_('Access Denied: Cannot delete Gate Entry linked to confirmed Purchase Order. Only Administrator can delete.'))
        return super(InwardOperation, self).unlink()


class OutwardGateEntry(models.Model):
    _inherit = 'outward.gate.entry'

    def unlink(self):
        """Block deletion of outward gate entries linked to confirmed sale orders"""
        for record in self:
            if record.sale_order_id and record.sale_order_id.state in ['sale', 'done']:
                # Check if user is admin/superuser OR has Administration access
                if not (self.env.user._is_superuser() or self.env.user.has_group('base.group_system') or self.env.user._is_admin()):
                    raise AccessError(_('Access Denied: Cannot delete Gate Entry linked to confirmed Sale Order. Only Administrator can delete.'))
        return super(OutwardGateEntry, self).unlink()