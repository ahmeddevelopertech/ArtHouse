from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_partner_ledger(self):
        """Open the partner ledger report across all branches"""
        self.ensure_one()

        # البحث عن تقرير دفتر الأستاذ الصحيح
        report = self.env['ir.model.data'].search([
            ('model', '=', 'account.report'),
            ('name', 'in', ['partner_ledger', 'account_report_partner_ledger'])
        ], limit=1)

        if report:
            report_id = report.res_id
            report_model = 'account.report'
            report_name = 'account_reports.partner_ledger'
        else:
            # استخدام الافتراضي إذا لم يتم العثور على التقرير
            report_id = self.env.ref('account_reports.partner_ledger', raise_if_not_found=False)
            if report_id:
                report_id = report_id.id
                report_model = 'account.report'
                report_name = 'account_reports.partner_ledger'
            else:
                # الحل البديل إذا لم يتم العثور على التقرير
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Partner Ledger Across Branches',
                    'res_model': 'account.move.line',
                    'view_mode': 'tree,form',
                    'domain': [('partner_id', '=', self.id)],
                    'context': {
                        'search_default_partner_id': self.id,
                        'force_company': False
                    }
                }

        return {
            'type': 'ir.actions.client',
            'name': 'Partner Ledger Across Branches',
            'tag': 'account.report',
            'options': {
                'partner_ids': self.ids,
                'date_from': False,
                'date_to': False,
                'unfold_all': False,
                'hierarchy': True,
                'journals': [],
                'company_ids': self.env.companies.ids,
                'force_company': False,
            },
            'context': {
                'report_type': 'partner_ledger',
                'active_id': report_name,
                'active_model': report_model
            }
        }