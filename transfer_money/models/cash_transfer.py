from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class CashTransfer(models.Model):
    _name = 'cash.transfer'
    _description = 'Cash Transfer Between Branches'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    source_company_id = fields.Many2one(
        'res.company',
        string='From Branch',
        required=True,
        default=lambda self: self.env.company
    )
    dest_company_id = fields.Many2one(
        'res.company',
        string='To Branch',
        required=True,
        # domain="[('id', 'in', allowed_company_ids)]"
    )
    label = fields.Char()
    amount = fields.Float(string='Amount', required=True)
    source_journal_id = fields.Many2one(
        'account.journal',
        string='Source Cash Journal',
        domain="[('company_id', '=', source_company_id), ('type', 'in', ['cash', 'bank'])]"
    )
    dest_journal_id = fields.Many2one(
        'account.journal',
        string='Destination Cash Journal',
        domain="[('company_id', '=', dest_company_id), ('type', 'in', ['cash', 'bank'])]"
    )
    transfer_date = fields.Date(string='Date', default=fields.Date.today)

    # حقول مساعدة لعرض الفروع المسموح بها
    allowed_company_ids = fields.Many2many(
        'res.company',
        string='Allowed Companies',
        compute='_compute_allowed_companies',
        store=True
    )

    @api.depends('source_company_id')
    def _compute_allowed_companies(self):
        """حساب الفروع المسموح بها للمستخدم"""
        for record in self:
            # المستخدمون العاديون يرون فقط فرعهم
            allowed_companies = self.env.company.ids

            # إذا كان المستخدم في مجموعة "Cash Transfer Manager"، يرى جميع الفروع
            if self.env.user.has_group('custom_cash_transfer.group_cash_transfer_manager'):
                allowed_companies = self.env['res.company'].search([]).ids

            record.allowed_company_ids = [(6, 0, allowed_companies)]

    @api.onchange('source_company_id')
    def _onchange_source_company(self):
        if self.source_company_id:
            self.source_journal_id = False
            # إعادة تعيين الفرع الوجهة إذا لم يكن مسموحًا به
            if self.dest_company_id and self.dest_company_id.id not in self.allowed_company_ids.ids:
                self.dest_company_id = False

    @api.onchange('dest_company_id')
    def _onchange_dest_company(self):
        if self.dest_company_id:
            self.dest_journal_id = False
            # التحقق من وجود يوميات في الفرع الوجهة
            journals = self.env['account.journal'].search([
                ('company_id', '=', self.dest_company_id.id),
                ('type', 'in', ['cash', 'bank'])
            ])
            if not journals:
                return {
                    'warning': {
                        'title': _("Warning"),
                        'message': _(
                            "No cash/bank journals found in the destination branch. Please configure journals first."),
                    }
                }

    def action_transfer(self):
        self.ensure_one()

        # التحقق من صلاحيات المستخدم
        if not self.env.user.has_group('transfer_money.group_cash_transfer_manager'):
            if self.source_company_id != self.env.company or self.dest_company_id not in self.env.companies:
                raise AccessError(_(
                    "You don't have permission to transfer cash between branches.\n"
                    "Contact your administrator to get the required permissions."
                ))

        # التحقق من صحة البيانات
        if not self.source_journal_id or not self.dest_journal_id:
            raise UserError(_("Please select both source and destination journals!"))

        if not self.source_journal_id.cash_transfer_account_id or not self.dest_journal_id.cash_transfer_account_id:
            raise UserError(_("Please set a default account for the cash journals!"))

        if not self.source_company_id.inter_company_clearing_account_id or not self.dest_company_id.inter_company_clearing_account_id:
            raise UserError(_(
                "Inter-company clearing account is not configured for one of the branches!\n"
                "Go to: Company Settings → Inter-Company Settings"
            ))

        # 1. إنشاء القيد في الفرع المصدر
        move_vals_source = {
            'date': self.transfer_date,
            'journal_id': self.source_journal_id.id,
            'company_id': self.source_company_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.source_company_id.inter_company_clearing_account_id.id,
                    'debit': self.amount,
                    'credit': 0.0,
                    'name': self.label,
                    'company_id': self.source_company_id.id,
                }),
                (0, 0, {
                    'account_id': self.source_journal_id.cash_transfer_account_id.id,
                    'debit': 0.0,
                    'credit': self.amount,
                    'name': self.label,
                    'company_id': self.source_company_id.id,
                }),
            ]
        }
        source_move = self.env['account.move'].with_company(self.source_company_id.id).create(move_vals_source)
        source_move.action_post()

        # 2. إنشاء القيد في الفرع المستلم
        self._create_counterpart_entry_in_destination_branch()

        # 3. عرض رسالة نجاح وإغلاق النافذة تلقائيًا
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success!'),
                'message': _(
                    'Transfer of %(amount)s recorded successfully.\n'
                    'The counterpart entry has been created in %(dest_branch)s.',
                    amount=self.amount,
                    dest_branch=self.dest_company_id.name
                ),
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }

    def _create_counterpart_entry_in_destination_branch(self):
        """إنشاء القيد المقابل في الفرع المستلم (الطريقة المضمونة لجميع إصدارات أودو 17)"""
        try:
            # إنشاء سياق جديد مع فرض الشركة المستهدفة
            new_context = dict(self.env.context, force_company=self.dest_company_id.id)

            # إنشاء القيد باستخدام السياق الجديد
            move_vals_dest = {
                'date': self.transfer_date,
                'journal_id': self.dest_journal_id.id,
                'company_id': self.dest_company_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.dest_journal_id.cash_transfer_account_id.id,
                        'debit': self.amount,
                        'credit': 0.0,
                        'name': self.label,

                        'company_id': self.dest_company_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.dest_company_id.inter_company_clearing_account_id.id,
                        'debit': 0.0,
                        'credit': self.amount,
                        'name': self.label,

                        'company_id': self.dest_company_id.id,
                    }),
                ]
            }

            # إنشاء القيد باستخدام السياق الجديد
            dest_move = self.env['account.move'].with_context(new_context).create(move_vals_dest)
            dest_move.action_post()

            return dest_move

        except Exception as e:
            # تسجيل الخطأ في السجلات
            self.env.cr.rollback()
            raise UserError(_(
                "Failed to create counterpart entry in destination branch:\n%s",
                str(e)
            )) from None
