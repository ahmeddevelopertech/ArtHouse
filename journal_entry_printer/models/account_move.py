from odoo import models, api
from num2words import num2words
import re


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_journal_entry(self):
        """Print the enhanced simplified journal entry report"""
        return self.env.ref('journal_entry_printer.action_report_account_move_custom_simplified').report_action(self)

    def _get_amount_in_words(self):
        """Convert amount to words in Arabic"""
        self.ensure_one()
        amount = sum(self.line_ids.mapped('debit'))
        try:
            # تحويل المبلغ إلى كلمات بالعربية
            words = num2words(amount, lang='ar', to='currency', currency='EGP')

            # تنظيف النص وإصلاح بعض المشكلات الشائعة
            words = words.replace("فقط", "")
            words = re.sub(r'\s+', ' ', words)
            words = words.capitalize()

            return words
        except:
            return ""

    def read(self, fields=None, load='_classic_read'):
        """Override to add amount in words to the record"""
        result = super(AccountMove, self).read(fields, load)

        # إضافة حقل amount_total_words إذا تم طلبه
        if fields and 'amount_total_words' in fields:
            for record in result:
                move = self.browse(record['id'])
                record['amount_total_words'] = move._get_amount_in_words()

        return result