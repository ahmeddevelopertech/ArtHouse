{
    'name': 'Create Manufacturing Order from Invoice Manual',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Auto-create manufacturing order with BOMs from confirmed invoice',
    'depends': ['account', 'mrp', 'manufacturing_custom'],
    'data': [
        'views/account_move_views.xml',
        'views/mrp_production_views.xml',  # Add this line

    ],
    'installable': True,
    'auto_install': False,
}
