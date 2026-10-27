from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        result = super(ResUsers, self).write(vals)
        # Check if x_gate_entry_manager field was updated
        if 'x_gate_entry_manager' in vals:
            gate_group = self.env.ref('gate_pass.group_gate_pass_manager')
            for user in self:
                if hasattr(user, 'x_gate_entry_manager') and user.x_gate_entry_manager == 'manager':
                    # Add user to gate pass manager group (only for manager)
                    if user.id not in gate_group.users.ids:
                        gate_group.write({'users': [(4, user.id)]})
                else:
                    # Remove user from gate pass manager group (when no selection)
                    if user.id in gate_group.users.ids:
                        gate_group.write({'users': [(3, user.id)]})
        return result