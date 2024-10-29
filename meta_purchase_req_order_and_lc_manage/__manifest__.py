{
    'name': 'Manage Purchase Order And LC',
    'summary': ''' 
            This Apps Help To Set Automating The Purchase Request ID And Lc Management ID
        ''',
    "description": """This Apps Help To Set Automating The Purchase Request ID And Lc Management ID""",
    'author': 'Metamorphosis, ''Joayanto',
    'company': 'Metamorphosis Limited',
    'license': 'AGPL-3',
    'website': 'http://metamorphosis.com.bd/',
    'category': 'Tools',
    'sequence': 1,
    'version': '17.0.0.1',
    'depends': [
        'base',
        'purchase',
        'purchase_request',
        'mail',
        'stock_account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/purchase_request_view.xml',
        'views/purchase_order_views.xml',
        'views/lc_manage_view.xml',
        'views/landed_cost_view.xml',
        'views/purchase_request_line_make_purchase_order_wizard_view.xml',
        # 'backend_assets.xml',
    ],
    # 'icon': "/meta_purchase_approval/static/description/icon.png",
    'installable': True,
    "auto_install": False,
    'application': True,
    'price': 99.0,
    'currency': 'EUR',
}
