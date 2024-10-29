# -*- coding: utf-8 -*-
{
    'name': "CWPL Custom Purchase Report",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Metamorphosis LTD, Rifat Anwar",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd",
    'category': 'Tools/Tools',
    'version': '15.0.0.1',
    'depends': ['base','purchase','web','account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_a2w.xml',
        'views/custom_doc_tax_total.xml',
        'views/po_report.xml',
        'views/po_rfq_report.xml',
    ],
    
    "license":"AGPL-3",
    "sequence" : -15,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
