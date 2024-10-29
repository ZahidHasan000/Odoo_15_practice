{
    'name': 'Meta Purchase Order View Customization',
    'summary': 'Meta Purchase Order View Customization',
    'author': 'Metamorphosis, ''Joaynto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'purchase',
        'purchase_requisition',
        'meta_purchase_comparison_system'
    ],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'application': True
}