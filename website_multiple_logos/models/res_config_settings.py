# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    header_logo_ids = fields.One2many(
        related='website_id.header_logo_ids',
        readonly=False,
        string="Header Logos"
    )
