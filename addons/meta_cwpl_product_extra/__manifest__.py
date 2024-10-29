# -*- coding: utf-8 -*-
{
    'name': "Product Extra",

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
    
    'depends': ['base','product'],

    'data': [
        'security/ir.model.access.csv',
        'views/genset_brand_view.xml',
        'views/engine_brand_view.xml',
        'views/alternator_brand_view.xml',
        'views/product_extra_view.xml',
        
    ],
    "licence":'AGPL-3',
    "sequence" : -2,
    "application" : True,
    "installable" : True,
    "auto_install" : False,

}
