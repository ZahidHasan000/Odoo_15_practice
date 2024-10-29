{
    'name': 'Employee Loan Details',
    
    'summary': 'This Module Will help to keep record of employee loan details which will be available for per employee data "Loan Details" Tab',
    'description': 'This Module Will help to keep record of employee loan details which will be available for per employee data "Loan Details" Tab',

    'license':'AGPL-3',
    'category':'Tools/Tools',
    'version': '15.0.0.1',
    'co-author': 'Rifat Anwar',
    'author': 'Metamorphosis LTD, Rifat Anwar',
    'website': 'http://odoo.metamorphosis.com.bd/',

    'depends': [        
        'hr',
        'hr_payroll',
        'hr_contract'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_loan_details_view.xml',
    ],
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto-install': False,
}