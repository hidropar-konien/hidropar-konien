# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

{
    'name': 'Website Multiple Header Logos',
    'summary': 'Allows adding multiple, dynamic logos to the website header.',
    'version': '11.0.1.0.0',
    'category': 'Website',
    'author': 'Konien Yazılım ve Danışmanlık',
    'website': 'https://www.odoo.com',
    'license': 'AGPL-3',
    'depends': [
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/website_header_logo_views.xml',
        'views/res_config_settings_views.xml',
        'views/website_templates.xml',
    ],
    'installable': True,
    'application': False,
}
