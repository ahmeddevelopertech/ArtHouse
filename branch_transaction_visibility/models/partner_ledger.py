from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    all_company_sale_order_ids = fields.One2many(
        'sale.order', 'partner_id',
        string='All Sales Orders (All Branches)',
        compute='_compute_all_company_sales_orders',
        help='All sales orders across all branches'
    )

    all_company_invoice_ids = fields.One2many(
        'account.move', 'partner_id',
        string='All Invoices (All Branches)',
        compute='_compute_all_company_invoices',
        help='All invoices across all branches'
    )

    all_company_payment_ids = fields.One2many(
        'account.payment', 'partner_id',
        string='All Payments (All Branches)',
        compute='_compute_all_company_payments',
        help='All payments across all branches'
    )

    all_company_account_move_ids = fields.One2many(
        'account.move', 'partner_id',
        string='All Journal Entries (All Branches)',
        compute='_compute_all_company_account_moves',
        help='All journal entries across all branches'
    )

    @api.depends_context('uid')
    def _compute_all_company_sales_orders(self):
        for partner in self:
            # Get all sales orders across all branches
            partner.all_company_sale_order_ids = self.env['sale.order'].with_context(force_company=False).search(
                [('partner_id', '=', partner.id)],
                order='date_order desc'
            )

    @api.depends_context('uid')
    def _compute_all_company_invoices(self):
        for partner in self:
            # Get all customer invoices across all branches
            partner.all_company_invoice_ids = self.env['account.move'].with_context(force_company=False).search(
                [('partner_id', '=', partner.id),
                 ('move_type', 'in', ['out_invoice', 'out_refund'])],
                order='invoice_date desc'
            )

    @api.depends_context('uid')
    def _compute_all_company_payments(self):
        for partner in self:
            # Get all customer payments across all branches
            partner.all_company_payment_ids = self.env['account.payment'].with_context(force_company=False).search(
                [('partner_id', '=', partner.id),
                 ('partner_type', '=', 'customer')],
                order='date desc'
            )

    @api.depends_context('uid')
    def _compute_all_company_account_moves(self):
        for partner in self:
            # Get all journal entries across all branches
            partner.all_company_account_move_ids = self.env['account.move'].with_context(force_company=False).search(
                [('partner_id', '=', partner.id),
                 ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'entry'])],
                order='date desc, name desc'
            )

    def action_partner_ledger_all_companies(self):
        """Open partner ledger report across all branches"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'name': 'Partner Ledger Across All Branches',
            'tag': 'partner.ledger',
            'params': {
                'partner_id': self.id,
                'partner_name': self.name,
            },
        }