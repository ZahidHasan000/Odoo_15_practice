# -*- coding: utf-8 -*-
{
    'name': "Sale Order Line BDT Subtotal",

    'summary': """This Module will calculate the a pricelist wise subtotal conversion to Given currency rate""",

    'description': """This Module will calculate the a pricelist wise subtotal conversion to Given currency rate""",

    'maintainer': 'Metamorphosis',
    'author': "Metamorphosis,Rifat Anwar",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd",
    
    'category': 'Tools/Tools',
    'version': '15.0.0.1',
    "license":"AGPL-3",
    
    'depends': ['base','sale'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/sol_sbtotal.xml',
    ],
    
    "sequence" : -50,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
