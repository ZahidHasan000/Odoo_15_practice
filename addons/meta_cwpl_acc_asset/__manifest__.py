# -*- coding: utf-8 -*-
{
    'name': "Account Asset Extra",

    'summary': """
        """,

    'description': """
        
    """,

    'maintainer': 'Metamorphosis',
    'author': "Metamorphosis",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['base','account','account_asset'],
    
    'data': [
        # 'security/ir.model.access.csv',
        'views/asset_field_extra.xml',
    ],
    
    "license":"AGPL-3",
    "sequence" : -9,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
