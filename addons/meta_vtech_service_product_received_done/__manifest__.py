
{
    "name": "Service Product Received Done",
    "summary": "This Module Update The Received Quantity in Purchase",
    "version": "15.0.1.0.1",
    "author": "Metamorphosis, ""joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tools",
    "depends": [
        "purchase",
        "stock",
        "meta_approval_matrix_cross_world"
    ],
    'license': 'LGPL-3',
    "data": [
        'security/ir.model.access.csv',
        'data/service_po_item_seq.xml',
        'views/service_product_po_views.xml',
        'views/service_template.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}