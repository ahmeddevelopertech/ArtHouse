from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class AccountMoveInstallment(models.Model):
    _name = 'account.move.installment'
    _description = 'Invoice Installment'
    _order = 'due_date asc'

    move_id = fields.Many2one(
        'account.move',
        string='Invoice',
        required=True,
        ondelete='cascade'
    )
    due_date = fields.Date(
        string='Due Date',
        required=True
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        required=True
    )
    currency_id = fields.Many2one(
        related='move_id.currency_id',
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='move_id.partner_id',
        store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('due', 'Due'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue')
    ], string='Status', default='draft', compute='_compute_state', store=True)
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        readonly=True
    )
    display_name = fields.Char(
        string="Display Name",
        compute='_compute_display_name',
        store=True
    )

    @api.depends('partner_id', 'amount', 'currency_id', 'due_date')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.partner_id.name or ''}: {rec.amount} Due - {rec.due_date}"

    @api.depends('due_date', 'payment_id')
    def _compute_state(self):
        today = fields.Date.today()
        for installment in self:
            if installment.payment_id:
                installment.state = 'paid'
            elif installment.due_date < today:
                installment.state = 'overdue'
            elif installment.due_date == today:
                installment.state = 'due'
            else:
                installment.state = 'draft'

    @api.constrains('amount')
    def _check_positive_amount(self):
        for installment in self:
            if installment.amount <= 0:
                raise ValidationError(_("Installment amount must be positive"))

    @api.model
    def _cron_check_due_installments(self):
        """Cron job to handle due and overdue installments"""
        _logger.info("=== Starting Installment Due Date Check ===")
        today = fields.Date.today()

        # Get due installments
        due_installments = self.search([
            ('due_date', '=', today),
            ('state', 'in', ['draft', 'overdue'])
        ])

        # Get overdue installments (3+ days overdue)
        overdue_date = today - relativedelta(days=3)
        overdue_installments = self.search([
            ('due_date', '<', today),
            ('due_date', '>=', overdue_date),
            ('state', '=', 'overdue')
        ])

        # Process notifications
        due_installments._send_installment_notification()
        overdue_installments._send_overdue_notification()
        return True

    def _send_installment_notification(self):
        """Send notification for due installments"""
        for installment in self:
            accountant = installment.move_id._get_accountant()
            if accountant:
                # Create activity
                installment.move_id.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Installment Due: %s') % installment.move_id.name,
                    note=_('Installment of %s is due today for invoice %s') %
                         (installment.amount, installment.move_id.name),
                    user_id=accountant.id
                )

                # Send OdooBot notification
                body = _(
                    "Installment Due: %(amount)s for invoice %(invoice)s (Customer: %(customer)s)"
                ) % {
                           'amount': installment.amount,
                           'invoice': installment.move_id.name,
                           'customer': installment.move_id.partner_id.name
                       }

                self.env['mail.message'].create({
                    'subject': _("Installment Due: %s") % installment.move_id.name,
                    'body': body,
                    'model': 'account.move',
                    'res_id': installment.move_id.id,
                    'message_type': 'notification',
                    'subtype_id': self.env.ref('mail.mt_note').id,
                    'author_id': self.env.user.partner_id.id,
                    'partner_ids': [accountant.partner_id.id],
                })

    def _send_overdue_notification(self):
        """Send notification for overdue installments"""
        for installment in self:
            accountant = installment.move_id._get_accountant()
            if accountant:
                days_overdue = (fields.Date.today() - installment.due_date).days
                installment.move_id.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Overdue Installment: %s') % installment.move_id.name,
                    note=_('Installment of %s is %d days overdue for invoice %s') %
                         (installment.amount, days_overdue, installment.move_id.name),
                    user_id=accountant.id
                )

    def action_mark_as_paid(self):
        """Create and post a payment for the installment"""
        for installment in self:
           installment.state="paid"

        return True