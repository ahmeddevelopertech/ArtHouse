from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    installment_id = fields.Many2one(
        'account.move.installment',
        string='Installment',
        readonly=True
    )

    @api.model
    def create(self, vals):
        payment = super().create(vals)
        if payment.installment_id:
            payment.installment_id.payment_id = payment.id
        return payment