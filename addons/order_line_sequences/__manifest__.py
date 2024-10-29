# -*- coding: utf-8 -*-

{
    'name': "PO Line Sequence",

    'summary': """Propagates line sequence to PO Line.""",

    'description': """Propagates line sequence to PO Line.""",

    'maintainer': 'Metamorphosis, Rifat Anwar',
    'author': "Metamorphosis",
    'co-author': "Rifat Anwar",
    "website": "https://metamorphosis.com.bd",

    "category": "Tools/Tools",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    
    'depends': ['base','purchase'],
    'data': [
        # 'views/sale_order_view.xml',
        # 'views/stock_view.xml',
        # 'views/sale_order_document_view.xml',
        # 'views/report_picking_view.xml',
        'views/purchase_order_view.xml',
        'views/report_purchaseorder_document_view.xml',
    ],
    "sequence" : -12,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
