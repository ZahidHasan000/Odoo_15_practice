{
    'name': 'Product Cost Readonly By Group',
    'summary': 'Product Cost Readonly By Group',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'base',
        'product',
        'meta_approval_matrix_cross_world',
        # 'meta_purchase_comparison_system'
    ],
    'data': [
        'views/product_cost_readonly.xml',
    ],
    'installable': True,
    'application': True
}