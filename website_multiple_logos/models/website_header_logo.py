# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

from odoo import fields, models


class WebsiteHeaderLogo(models.Model):
    _name = 'website.header.logo'
    _description = 'Website Header Logo'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    logo = fields.Binary(string="Logo", required=True, attachment=True)
    url = fields.Char(string="URL", help="URL to redirect to when the logo is clicked.")
    website_id = fields.Many2one(
        'website',
        string="Website",
        ondelete='cascade',
        required=True,
        help="The website this logo belongs to."
    )
    active = fields.Boolean(default=True)
