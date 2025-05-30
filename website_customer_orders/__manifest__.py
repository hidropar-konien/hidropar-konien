# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

{
    'name': "Customer Orders Portal",
    'summary': """Customer Portal for viewing their sales orders and details.""",
    'description': """
        This module extends the Odoo portal to allow customers to view their
        sales orders with custom details including delivery status and expected dates.
    """,
    'author': "Konien Yazılım ve Danışmanlık",
    'website': "http://www.konien.com",
    'category': 'Website/E-commerce',
    'version': '11.0.1.0.0',
    'depends': ['portal', 'sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
        'report/website_customer_order_report.xml',
    ],
    'installable': True,
    'application': False,
}