# -*- coding: utf-8 -*-
{
    'name': "CRM & Lead Customization",

    'summary': """
        """,

    'description': """
        
    """,

    'maintainer': 'Metamorphosis',
    'author': "Metamorphosis",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd/",
    'category': 'Tools/Tools',
    'version': '15.0.0.1',
    'depends': ['crm','hr','sale_crm','sale','account','web'],
    
    'data': [
        # 'security/ir.model.access.csv',
        'security/crm_group_for_button.xml',
        'data/lead_sequence.xml',        
        'views/lead_extra_customization_view.xml',
        'views/lead_lst_view.xml',
        'views/lead_to_opp_extra_view.xml',
        'views/sale_team_readonly.xml',
    ],
    "license":"AGPL-3",
    "sequence" : 2,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
