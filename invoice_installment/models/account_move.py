from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    installment_ids = fields.One2many(
        'account.move.installment',
        'move_id',
        string='Installments'
    )
    has_installments = fields.Boolean(
        string='Has Installments',
    )
    installment_total = fields.Monetary(
        string='Installment Total',
        compute='_compute_installment_total',
        store=True
    )

    @api.depends('installment_ids.amount')
    def _compute_installment_total(self):
        for move in self:
            move.installment_total = sum(move.installment_ids.mapped('amount'))



    @api.constrains('installment_ids', 'amount_total')
    def _check_installment_total(self):
        for move in self:
            if move.installment_ids and not move.currency_id.is_zero(
                    move.installment_total - move.amount_total
            ):
                raise ValidationError(
                    _("Total installments (%s) must match invoice total (%s)") %
                    (move.installment_total, move.amount_total)
                )

    def action_post(self):
        """Override post action to schedule installment notifications"""
        res = super().action_post()
        self.action_schedule_installment_notifications()
        return res

    def action_schedule_installment_notifications(self):
        """Create scheduled activities for installments"""
        for move in self:
            for installment in move.installment_ids:
                # Only schedule future installments
                if installment.due_date >= fields.Date.today():
                    move.activity_schedule(
                        'mail.mail_activity_data_todo',
                        date_deadline=installment.due_date,
                        summary=_('Installment Due: %s') % move.name,
                        note=_('Installment of %s is due for invoice %s') %
                             (installment.amount, move.name),
                        user_id=move._get_accountant().id
                    )
        return True

    def _get_accountant(self):
        """Get the accountant user - defaults to invoice user"""
        # group = self.env.ref('account.group_account_manager')
        # return group.users[0] if group.users else self.env.user
        return self.invoice_user_id