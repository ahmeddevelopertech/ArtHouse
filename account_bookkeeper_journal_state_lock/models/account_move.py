from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        if vals.get('state') != self.state:
            if self.move_type not in ('out_invoice', 'out_refund'):
                print(self.move_type)
                if not self.env.user.has_group("account.group_account_manager"):
                    raise UserError(_("You must have permission to perform this action"))
        return super().write(vals)
