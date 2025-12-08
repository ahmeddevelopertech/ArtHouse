{
    'name': 'Stock Partial Delivery',
    'summary': 'Add Partial Delivery stage and a Delivered Products tab to picking',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'author': 'Your Name',
    'license': 'AGPL-3',
    'depends': ['stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
