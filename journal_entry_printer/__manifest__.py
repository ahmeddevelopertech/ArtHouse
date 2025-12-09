{
    'name': 'Journal Entry Printer',
    'version': '17.0.1.0.0',
    'author': 'Your Company',
    'category': 'Accounting/Accounting',
    'summary': 'Print journal entries across all branches with custom report format',
    'description': """
        This module enables accountants to print journal entries across all branches (companies).
        It provides a custom report format that shows detailed information about each journal entry.

        Features:
        - Print journal entries across branches
        - Custom report format with professional layout
        - Shows all journal entry details in a clear format
        - Works with multi-company environments
        - Simple integration with existing Odoo interface
    """,
    'depends': ['base', 'account'],
    'data': [
        'security/ir_rule.xml',
        'reports/account_move_report.xml',
        'reports/report_actions.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OEEL-1',
    'price': 0.0,
    'currency': 'EUR',
}