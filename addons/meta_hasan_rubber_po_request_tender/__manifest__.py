
{
    "name": "Changes of Purchase Request And Tender",
    "summary": "This Module changes the Purchase Request And Tender",
    "version": "14.0.1.0.1",
    "author": "Metamorphosis,""Joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tllos",
    "depends": [
        "base",
        'purchase',
        'purchase_request',
        'stock',
    ],
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        'views/purchase_request_inherit_view.xml',
        'views/purchase_tender_inherit_view.xml',
        # 'views/stock_quant_product_weight_view.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}