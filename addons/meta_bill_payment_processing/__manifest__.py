{
    'name': 'Meta Bill Payment Process Status',
    'summary': 'Meta Bill Payment Process Status',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'account',
        'meta_payment_reconcile_confirm',
        # 'meta_purchase_comparison_system'
    ],
    'data': [
        'views/account_move_payment_process_view.xml',
    ],
    'installable': True,
    'application': True
}