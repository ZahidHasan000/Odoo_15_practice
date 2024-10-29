
{
    "name": "Easy Way to Create PO Tender PR Etc",
    "summary": "This Module Create PO PR Tender in the Another Model",
    "version": "15.0.1.0.1",
    "author": "Metamorphosis, ""joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tools",
    "depends": [
        "purchase",
        "sale",
        "purchase_requisition",
        "purchase_request",
        "meta_sale_order_bom_customization",
        "meta_approval_matrix_cross_world",
        "meta_crm_so_extra",
        'hr',
        'meta_pr_select_in_stock_picking'
    ],
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        'views/create_tender_view.xml',
        'views/create_sale_order_view.xml',
        'views/purchase_request_search_inherit.xml',
        'views/stock_location_inherited_view.xml',
        'wizard/product_add_wizard_view.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}