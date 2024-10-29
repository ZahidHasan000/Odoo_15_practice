{
    'name': "Pinnacle Seven Employee Approvals",

    'summary': """
        This module provide Approvals for Employee Master.""",
    'description': """
        Once employee is created it will not be visible to anyone, after approval only it will be visible evrywhere.
    """,
    'author': "Pinnacle Seven Pvt. Ltd.",
    'website': "https://www.pinnacleseven.com/",
    'category': 'Employee',
    'version': '0.1',
    'depends': ['base','hr', 'hr_appraisal'],
    'data': [
        'security/ir.model.access.csv',
        'security/access_rights.xml',
        'data/to_approve_mail_temp.xml',
        'data/approved_mail_temp.xml',
        'data/rejected_mail_temp.xml',
        'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/rejection_wizard.xml',
    ],
    'images': ['static/description/images/banner.png'],
    'installable': True,
    'application': True,
    'license': 'AGPL-3'
}
