
{
    "name": "Budget Product Costing Sales",
    "summary": "Budget Product Costing Sales",
    "version": "15.0.1.0.1",
    "author": "Metamorphosis, ""Joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tllos",
    "depends": [
        "sale",
    ],
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        'security/budget_showing_group.xml',
        'views/inherit_sale_order_line.xml',
        'views/product_costing_view.xml',
        'views/chatter_view.xml',
        # 'views/create_sale_order_view.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}