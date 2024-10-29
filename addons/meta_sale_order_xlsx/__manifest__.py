# -*- coding: utf-8 -*-
{
    'name': "Sale Order Excel Report",

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
    'depends': ['sale', 'report_xlsx'],

    'data': [
        # 'security/ir.model.access.csv',
        # 'security/so_extra_record_rule.xml',
        'report/sale_order_report_xlsx.xml'
    ],
    "license": "AGPL-3",
    "sequence": -10,
    "application": True,
    "installable": True,
    "auto_install": False,
}
