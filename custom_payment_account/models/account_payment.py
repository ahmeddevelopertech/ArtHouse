from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Field to store the journal's "tree account" (auto-filled)
    tree_account_id = fields.Many2one(
        'account.account',
        string='Tree Account',
        compute='_compute_tree_account',
        store=True,
        readonly=True,
        help="Auto-selected child account of the journal's default account"
    )

    @api.depends('journal_id')
    def _compute_tree_account(self):
        for payment in self:
            # Reset if no journal selected
            if not payment.journal_id:
                payment.tree_account_id = False
                continue

            # Get the journal's default account (e.g., "101000 Bank")
            default_account = payment.journal_id.default_account_id

            # Find the FIRST child account under the default account
            child_account = self.env['account.account'].search([
                ('parent_id', '=', default_account.id),
                ('company_id', '=', payment.company_id.id),
                ('deprecated', '=', False)
            ], limit=1)

            # Assign the child account (e.g., "101001 USD Account")
            payment.tree_account_id = child_account.id if child_account else default_account.id

    # OVERRIDE: Force payment to use the tree account
    def _get_payment_move_lines(self, amount):
        lines = super()._get_payment_move_lines(amount)
        for line in lines:
            # Replace journal's default account with the tree account
            if line['account_id'] == self.journal_id.default_account_id.id:
                line['account_id'] = self.tree_account_id.id
        return lines