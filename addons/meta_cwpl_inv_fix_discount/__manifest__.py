# -*- coding: utf-8 -*-
{
    'name': "Invoice Fix Discount From Sale order",

    'summary': """This Module will be helpful for to continue the given fix discount in invoice from the sale order""",

    'description': """This Module will be helpful for to continue the given fix discount in invoice from the sale order""",

    'maintainer': 'Metamorphosis',
    'author': "Metamorphosis",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd",
    'category': 'Tools/Tools',
    'version': '15.0.0.1',
    'depends': ['meta_crm_so_extra','account'],
    
    'data': [
        # 'security/ir.model.access.csv',
        'views/inv_fix_disc_view.xml',
        'views/so_fix_discount.xml',
    ],
    "license":"AGPL-3",
    "sequence" : -10,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
