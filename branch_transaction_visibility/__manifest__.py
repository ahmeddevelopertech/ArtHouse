{
    'name': 'Branch Transaction Visibility',
    'version': '17.0.1.0.0',
    'author': 'Your Company',
    'category': 'Accounting/Accounting',
    'summary': 'Allow accountants to see customer transactions across all branches',
    'description': """
        This module enables accountants to view customer transactions across all branches (companies).
        When a customer makes a purchase at one branch and pays at another, the transaction will be visible
        to all accountants regardless of their branch.

        Features:
        - View all sales orders across branches
        - View all invoices across branches
        - View all payments across branches
        - View all journal entries across branches
        - Partner Ledger report across branches (using standard Odoo report)
        - Special tab in customer form showing cross-branch transactions
        - Secure implementation with proper access controls
    """,
    'depends': ['base', 'sale', 'account', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # 'views/res_partner_views.xml',
        # 'views/account_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OEEL-1',
    'price': 0.0,
    'currency': 'EUR',
}   