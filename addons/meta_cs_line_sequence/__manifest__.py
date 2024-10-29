# -*- coding: utf-8 -*-

{
    'name': "CS Line Sequence",

    'summary': """Propagates line sequence to CS Line.""",

    'description': """Propagates line sequence to CS Line.""",

    'maintainer': 'Metamorphosis, Rifat Anwar',
    'author': "Metamorphosis",
    'co-author': "Rifat Anwar",
    "website": "https://metamorphosis.com.bd",

    "category": "Tools/Tools",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    
    "depends": ['purchase_request','meta_easy_way_create_and_view','meta_purchase_comparison_system'],
    "data": [
        "views/cs_view.xml",
        # "views/report_pr.xml",
        ],
    "post_init_hook": "post_init_hook",
    
    "sequence" : -11,
    "application" : True,
    "installable" : True,
    "auto_install" : False,
}
