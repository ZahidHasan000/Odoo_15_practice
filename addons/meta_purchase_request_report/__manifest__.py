
{
    "name": "Purchase Request Report",
    "summary": "This Module Create PR PDF Report",
    "version": "15.0.1.0.1",
    "author": "Metamorphosis, ""joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tllos",
    "depends": [
        "purchase_requisition",
    ],
    "license": "LGPL-3",
    "data": [
        'reports/request_reports.xml',
        'reports/purchase_request_template.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}