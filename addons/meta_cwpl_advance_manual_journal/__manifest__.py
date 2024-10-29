{
    'name': 'Create Journal In Advance Payment',
    'summary': 'Create Journal In Advance Payment',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'account',
        'hr',
        'meta_cwpl_adv_employee',
    ],
    'data': [
        'views/employee_advance_inherit_view_form.xml',
        'views/account_journal_view.xml',
    ],
    'installable': True,
    'application': True
}
