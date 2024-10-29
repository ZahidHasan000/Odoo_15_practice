
{
    "name": "Inventory Valuation Add Categories Valuation Account",
    "summary": """Here This Module Work Base On Inventory Valuation 
            Tree or From View add Field Category and Stock Valuation Account
            """,
    "version": "14.0.1.0.1",
    "author": "Metamorphosis," "Joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tools",
    "depends": [
        "base", 'stock', 'stock_account'
    ],
    "license": "LGPL-3",
    "data": [
        'views/inventory_valuation_inherit.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}