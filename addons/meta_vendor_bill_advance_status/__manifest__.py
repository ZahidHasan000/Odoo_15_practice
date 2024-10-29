{
    'name': 'Meta Vendor Bill Advance Status',
    'summary': 'Meta Vendor Bill Advance Status',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'account', 'purchase', 'purchase_down_payment'
    ],
    'data': [
        'views/bill_status_view.xml',
        # 'views/register_payment_inherit_view.xml',
    ],
    'installable': True,
    'application': True
}