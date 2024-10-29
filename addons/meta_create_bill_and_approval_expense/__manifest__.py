{
    'name': 'Meta Create Bill From Expense and add Approval',
    'summary': 'Meta Create Bill From Expense and add Approval',
    'author': 'Metamorphosis, ''Joyanto',
    'license': 'AGPL-3',
    'website': 'https://metamorphosis.com.bd/',
    'category': 'Tools/Tools',
    'sequence': 1,
    'version': '15.0.1.0.0',
    'depends': [
        'account',
        'hr_expense',
        # 'meta_purchase_comparison_system'
    ],
    'data': [
        'data/expense_sequence.xml',
        'views/hr_expense_sheet_from_view1.xml',
    ],
    'installable': True,
    'application': True
}