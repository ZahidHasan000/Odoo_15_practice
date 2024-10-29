{
    'name': 'Purchase Request Message log',
    'summary': 'Purchase Request Message log',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'purchase_request',
    ],
    'data': [
        'views/pr_message_template.xml',
        'views/pr_line_message_template.xml',
    ],
    'installable': True,
    'application': True
}