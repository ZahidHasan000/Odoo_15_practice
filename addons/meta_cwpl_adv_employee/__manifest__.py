# -*- coding: utf-8 -*-
{
    'name': "Advance To Employee",

    'summary': """
        Advance To Employee""",

    'description': """
        Advance To Employee
    """,

    'maintainer': 'Metamorphosis LTD',
    'author': "Metamorphosis LTD, Rifat Anwar",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd",

    'category': 'Tools/Tools',
    'version': '15.0.0.1',

    'depends': ['base','account','hr', 'meta_approval_matrix_cross_world'],
    'data': [
        'security/ir.model.access.csv',
        'data/emp_adv_seq.xml',
        'views/employee_advance_view.xml',
        'views/account_move_extra.xml',
    ],
    
    "license":"AGPL-3",
    "sequence" : -8,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
    
}
