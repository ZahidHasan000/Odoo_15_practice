
{
    "name": "BOM show in sale order line",
    "summary": "BOM show in sale order line",
    "version": "15.0.1.0.1",
    "author": "Metamorphosis, ""joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tools",
    "depends": [
        "sale",
        "mrp",
    ],
    "license": "LGPL-3",
    "data": [
        'views/inherit_sale_order_form_view2.xml',
        'views/inherit_mrp_production_form_view1.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}