{
    'name': "History movement report",
    'version': '15.0.1.0.0',
    'summary': 'Can use only selected location with date for products history.',
    'description': 'We can create pdf report for the selected location from start date to end date of products',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/location_wizard.xml',
        'wizard/location_wizard_template.xml',
        'wizard/output_wizard_template.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
