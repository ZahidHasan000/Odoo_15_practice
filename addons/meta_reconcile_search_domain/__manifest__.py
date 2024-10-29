{
    'name': 'Meta Reconcile Search Domain',
    'summary': 'Meta Reconcile Search Domain',
    'author': 'Metamorphosis, ''Joaynto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'account_accountant', 'meta_check_number_showing_in_journal_item'
    ],
    'data': [
        # 'views/check_number_in_move_line_item.xml'
    ],
    'assets': {
        'web.assets_qweb': [
            'meta_reconcile_search_domain/static/src/xml/*',
        ],
    },
    'installable': True,
    'application': True
}