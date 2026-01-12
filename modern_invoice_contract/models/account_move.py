from odoo import fields, models
from odoo.exceptions import AccessError
from odoo.tools.misc import format_date, formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_contract_installments(self):
        """Return installments for report rendering.

        Notes:
        - Do NOT use getattr()/hasattr() inside QWeb (safe eval may block them).
        - Do NOT pass lang_code to formatLang in Odoo 17.
        """
        self.ensure_one()

        if "installment_ids" not in self._fields:
            return []

        try:
            installments = self.installment_ids
        except AccessError:
            return []

        if not installments:
            return []

        installments = installments.sorted(lambda r: (r.due_date or fields.Date.max, r.id))

        try:
            selection = self.env["account.move.installment"]._fields["state"].selection
            state_labels = dict(selection)
        except Exception:
            state_labels = {}

        currency = self.currency_id

        res = []
        for i, inst in enumerate(installments, start=1):
            date_str = format_date(self.env, inst.due_date) if inst.due_date else ""
            amount_str = (
                formatLang(self.env, inst.amount, monetary=True, currency_obj=currency)
                if currency else str(inst.amount)
            )
            res.append({
                "name": inst.display_name or f"Installment {i}",
                "date": date_str,
                "amount_formatted": amount_str,
                "state": state_labels.get(inst.state, inst.state),
            })
        return res
