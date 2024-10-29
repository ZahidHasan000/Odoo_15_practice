# -*- coding: utf-8 -*-
{
    'name': "CRM Sale Order Extra",

    'summary': """
        """,

    'description': """
        
    """,

    'maintainer': 'Metamorphosis',
    'author': "Metamorphosis",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd",
    'category': 'Tools/Tools',
    'version': '15.0.0.1',
    'depends': ['base','sale_stock','meta_cwpl_lead_extra','meta_approval_matrix_cross_world','sale'],
    
    'data': [
        # 'security/ir.model.access.csv',
        'security/so_extra_record_rule.xml',
        'views/crm_so_extra_view.xml',
        # 'views/custom_so_line.xml',
        'views/other_report_custom.xml',
        'views/so_report.xml',
    ],
    "license":"AGPL-3",
    "sequence" : -10,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
