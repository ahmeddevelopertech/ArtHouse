from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    inter_company_clearing_account_id = fields.Many2one(
        'account.account',
        string='Inter-Company Clearing Account',
        domain="[('company_id', '=', id)]",
        help="Account used for inter-branch cash transfers"
    )

    # الحقول الجديدة (ضرورية للربط بين الفروع)
    counterpart_company_id = fields.Many2one(
        'res.company',
        string='Counterpart Company',
        help="The company that is counterpart for inter-company transactions"
    )
    counterpart_account_id = fields.Many2one(
        'account.account',
        string='Counterpart Account',
        domain="[('company_id', '=', counterpart_company_id)]",
        help="The account in the counterpart company"
    )