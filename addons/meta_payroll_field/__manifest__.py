
{
    "name": "Payroll Extra Field",
    "summary": "This Module add Mobile Allowance ",
    "version": "14.0.1.0.1",
    "author": "Metamorphosis",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools",
    "depends": [
        "base",
        "hr_contract",
        "hr_payroll",
    ],
    "license": "LGPL-3",
    "data": [
        'views/contract.xml',
        'views/payslip.xml',
        'views/employee.xml',
        # 'views/report_payslip.xml',
        'views/rule.xml',
        'views/salary_rule_tree.xml',
    ],
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}
