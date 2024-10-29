
{
    "name": "Landed Cost PO and LC Number Show",
    "summary": "Landed Cost PO and LC Number Show",
    "version": "15.0.1.0.1",
    "author": "Metamorphosis, ""joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Inventory/Inventory",
    "depends": [
        "purchase",
        "stock",
        "stock_landed_costs",
    ],
    "license": "LGPL-3",
    "data": [
        'views/landed_cost_inherit_view.xml',
        # 'views/create_sale_order_view.xml',
        # 'views/purchase_request_search_inherit.xml',
        # 'views/stock_location_inherited_view.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}