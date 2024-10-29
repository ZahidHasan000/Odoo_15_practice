{
    'name': 'Purchase LC Rate Manual',
    'summary': 'Purchase LC Rate Manual',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'purchase',
        'purchase_stock',
        'meta_approval_matrix_cross_world',
        'purchase_down_payment',
    ],
    'data': [
        'views/purchase_order_lc_currency_view.xml',
    ],
    'installable': True,
    'application': True
}