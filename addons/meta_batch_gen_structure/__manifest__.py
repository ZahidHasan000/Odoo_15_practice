# -*- coding: utf-8 -*-
{
    'name': "Batch Generation Employee List Extend ",

    'summary': """
        It will help to get employees with structure domain.
        """,

    'description': """
        It will help to get employees with structure domain.
    """,

    'author': "Metamorphosis",
    'co-author': "Rifat Anwar",
    'website': "https://metamorphosis.com.bd/",
    'category': 'Uncategorized',
    'version': '15.0.0.0',
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'hr_payroll',
        'web',
        'meta_salary_report'
        ],
    
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_extend.xml',
        'views/hr_payslip_custom.xml',
        # 'views/employee_with_structure_batch.xml',
        # 'views/templates.xml',
    ],
    "sequence":0,
    "application"          :  True,
    "installable"          :  True,
    "auto_install"         :  False,
}
