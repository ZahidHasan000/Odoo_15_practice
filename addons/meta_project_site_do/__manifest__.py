{
    'name': 'Meta Project Site PO select receipt id in DO',
    'summary': 'Meta Project Site PO select receipt id in DO',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'sale_stock',
        'stock',
        'purchase_stock'
    ],
    'data': [
        'views/project_site_stock_picking_do_view.xml',
        # 'views/stock_picking_inherit_view.xml',
    ],
    'installable': True,
    'application': True
}