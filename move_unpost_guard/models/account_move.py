from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    # Customer invoices + their refunds are exempt from this extra restriction.
    _UNPOST_EXEMPT_MOVE_TYPES = ("out_invoice", "out_refund")

    def _check_unpost_rights(self):
        """Block unpost (posted -> draft) for non-account-managers except for customer invoices/refunds."""
        forbidden = self.filtered(
            lambda m: m.state == "posted" and m.move_type not in self._UNPOST_EXEMPT_MOVE_TYPES
        )
        if forbidden and not self.env.user.has_group("account.group_account_manager"):
            raise UserError(_("You must have permission to unpost this entry."))

    def button_draft(self):
        # Canonical Unpost entrypoint
        self._check_unpost_rights()
        return super().button_draft()

    def write(self, vals):
        # Prevent bypass via direct write to state='draft'
        # Only guard the specific Unpost transition request.
        if vals.get("state") == "draft":
            self._check_unpost_rights()
        return super().write(vals)
