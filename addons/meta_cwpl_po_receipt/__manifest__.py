# -*- coding: utf-8 -*-
{
    'name': "Purchase Receipt Report",

    'summary': """ """,

    'description': """ """,

    'maintainer': 'Metamorphosis LTD',
    'author': "Metamorphosis LTD, Rifat Anwar",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd/",
    'category': 'Tools/Tools',
    'version': '15.0.0.1',
    'depends': ['base','stock'],

    'data': [
        # 'security/ir.model.access.csv',
        'report/po_receipt_report.xml',
        'report/po_receipt_report_template.xml',
    ],
    "license":"AGPL-3",
    "sequence" : -9,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
    
}
