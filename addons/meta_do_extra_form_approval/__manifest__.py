{
    'name': 'Meta Delivery Orders Extra Form Approval',
    'summary': 'Meta Delivery Orders Extra Form Approval',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'sale',
        'sale_stock',
        'stock',
        'purchase_stock',
        # 'meta_purchase_comparison_system'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/do_form_approval.xml',
        'views/stock_picking_inherit_view.xml',
    ],
    'installable': True,
    'application': True
}