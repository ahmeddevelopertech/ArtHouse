from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    cash_transfer_account_id = fields.Many2one(
        'account.account',
        string='Cash Transfer Account',
        domain="[('account_type', 'in', ['asset_cash', 'asset_current'])]",
        help="Account used specifically for inter-branch cash transfers. If not set, the journal's default account will be used."
    )