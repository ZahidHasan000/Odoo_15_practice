{
    'name': 'Aristo Inventory Movement Report',
    'summary': 'Aristo Inventory Movement Report',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/inventory_movement_wizard.xml',
        'reports/inventory_report.xml',
        'reports/location_wise_products_movement_details.xml',
        'reports/product_wise_all_location_stock_report.xml',
        'reports/product_details_location_report.xml',
    ],
    'installable': True,
    'application': True
}