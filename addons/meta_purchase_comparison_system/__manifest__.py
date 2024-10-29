
{
    "name": "Purchase Comparison System",
    "summary": "This Module Compare Product in Ther Tender",
    "version": "14.0.1.0.1",
    "author": "Metamorphosis, ""joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tllos",
    "depends": [
        "base",
        "purchase",
        "purchase_requisition",
        "purchase_request",
        "meta_hasan_rubber_po_request_tender",
        "meta_easy_way_create_and_view"
    ],
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        'security/compare_approval_groups.xml',
        'data/comparison_seq.xml',
        'views/comparison_views.xml',
        'views/tender_view.xml',
        'views/template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'meta_purchase_comparison_system/static/src/css/comparison.css',
            'meta_purchase_comparison_system/static/src/js/components/comparisondata.js'
        ],
        'web.assets_qweb': [
            'meta_purchase_comparison_system/static/src/js/components/comparison_data.xml',
        ],
    },
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}