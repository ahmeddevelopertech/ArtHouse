{
    'name': 'Invoice Installment Management',
    'version': '17.0.2.0.0',
    'category': 'Accounting',
    'summary': 'Manage invoice installments with notifications',
    'description': """
        Add installment options to customer invoices with due date notifications
        for accountants
    """,
    'depends': ['account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/installment_views.xml',
        'data/cron_data.xml',

    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
