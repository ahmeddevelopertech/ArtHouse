from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # الحقل الذي كنا نفتقده (مهم جدًا)
    is_inter_company_transaction = fields.Boolean(
        string='Inter-Company Transaction',
        default=False,
        help="Mark this line as part of an inter-company transaction"
    )