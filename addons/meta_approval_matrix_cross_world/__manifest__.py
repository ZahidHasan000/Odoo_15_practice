{
    'name': 'Approval Matrix',
    'summary': 'All Approval are Work are Done This Apps',
    'author': 'Metamorphosis, ''Joaynto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'account',
        'sale',
        'purchase',
        'purchase_request',
        'repair'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/service_seq.xml',
        'security/all_approval_group.xml',
        'views/invoice_view.xml',
        'views/sale_quotation_view.xml',
        'views/purchase_request_view.xml',
        'views/purchase_quotation_view.xml',
        'views/payment_approval_view.xml',
        'views/repair_view_inherit.xml',
        # 'views/stock_picking_transfer_view.xml',
    ],
    'installable': True,
    'application': True
}