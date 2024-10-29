{
    'name': 'Salary Report',
    'summary': 'This Module is changes the reports Format',
    'author': 'Metamorphosis',
    'license': 'AGPL-3',
    'website': 'http://odoo.metamorphosis.com.bd/',
    'category': 'Report',
    'sequence': 1,
    'version': '13.0.1.0.0',
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'hr_payroll',
        'report_xlsx',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/payslip.xml',
        'views/employee.xml',
        'views/contract.xml',
        'report/employee_salary_report.xml',
        'report/report.xml',
        'wizard/report_salary.xml',
        'views/structure.xml',

    ],
    'installable': True,
    'application': True,
}