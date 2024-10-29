{
    'name': 'Meta Customer Invoice Advance Status',
    'summary': 'This module adds a new field in account move to have a custom status to find out the invoices with downpayment.',
    'author': 'Metamorphosis, ''Rifat Anwar',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.0.1',
    'depends': [
        'account',
        'sale',
        'meta_crm_so_extra'
    ],
    'data': [
        'views/inv_status_view.xml',
    ],
    'installable': True,
    'application': True
}