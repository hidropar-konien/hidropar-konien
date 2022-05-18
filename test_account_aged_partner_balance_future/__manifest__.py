{
    'name': "Test Account Aged Partner Balance Future and Past Function",
    'summary': """
        Test Account Aged Partner Balance Future and Past Function""",
    'author': "İsmail Eski",
    "website": "https://github.com/ieski",
    'category': 'account',
    "version": "11.0.1.0.0",
    'depends': ['base', 'account'],
    'data': [
        'wizard/account_report_aged_partner_balance_new_view.xml',
        'views/report_agedpartnerbalance.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
