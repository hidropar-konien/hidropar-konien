# -*- coding: utf-8 -*-
# Copyright 2020 Konien Ltd.Şti.

{
    'name': 'Account Aged Partner Currency Balance',
    'summary': 'Account Aged Partner Currency Balance',
    'version': '1.0.0',
    'category': 'account',
    'website': 'https://www.konien.com',
    'author': 'Konien Yazılım ve Danışmanlık Dış Tic. Ltd. Şti.',
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/icon.png'],
    'depends': ['base', 'account'],
    'external_dependencies': {
    },
    'data': [
        'wizard/account_report_aged_partner_currency_balance.xml',
        'views/report_agedpartnerbalance.xml',
    ],
}
