# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

from odoo import fields, models

class Website(models.Model):
    _inherit = 'website'

    header_logo_ids = fields.One2many(
        'website.header.logo',
        'website_id',
        string="Header Logos",
        help="Logos to be displayed in the website header."
    )
