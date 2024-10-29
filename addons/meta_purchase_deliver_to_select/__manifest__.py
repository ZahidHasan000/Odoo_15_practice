{
    'name': 'Purchase Deliver to Select',
    'summary': 'Purchase Deliver to Select',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'http://metamorphosis.com.bd/',
    'category': 'Report',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'purchase', 'meta_approval_matrix_cross_world', 'purchase_stock'
    ],
    'data': [
        'views/purchase_order_deliver_to_view.xml',
    ],
    'installable': True,
    'application': True,
}