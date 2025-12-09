{
    'name': 'Cash Transfer Between Branches',
    'version': '2.0',
    'summary': 'Transfer cash between branches with custom cash transfer accounts',
    'description': """
        This module allows transferring cash between different branches (companies)
        and automatically creates counterpart entries in the destination branch.
        It includes a custom cash transfer account for each journal.
    """,
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'views/res_company_views.xml',
        'views/account_journal_views.xml',  # ← إضافة ملف العرض الجديد
        'views/cash_transfer_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
