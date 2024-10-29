{
    'name': 'Meta Advance Bill Confirm Specific User',
    'summary': 'Meta Advance Bill Confirm Specific User',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'account', 'meta_approval_matrix_cross_world',
    ],
    'data': [
        'security/advance_bill_confirm_group.xml',
        # 'views/register_payment_inherit_view.xml',
    ],
    'installable': True,
    'application': True
}