# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

from odoo import api, fields, models, _


class AccountCommonReport(models.TransientModel):
    _inherit = "account.common.report"

    currency_id = fields.Many2one('res.currency', 'Currency')
    direction_selection = fields.Selection([('past', 'Past'), ('future', 'Future')], "Direction Selection", default='past')
    partner = fields.Many2one('res.partner', 'Partner')

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        result['currency_id'] = data['form']['currency_id'] or False
        result['direction_selection'] = data['form']['direction_selection'] or False
        result['currency_id'] = data['form']['partner'] or False
        return result

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'currency_id', 'direction_selection', 'partner'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self._print_report(data)


