# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

from odoo import api, fields, models, _
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class AccountCommonReport(models.TransientModel):
    _inherit = "account.common.report"

    period_length = fields.Integer(string='Period Length (days)', required=True, default=30)
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
        result['partner'] = data['form']['partner'][0] or False
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

    def pre_print_report(self, data):
        # data['form'].update(self.read(['result_selection'])[0])
        data['form'].update(self.read(['partner'])[0])
        data['form'].update(self.read(['direction_selection'])[0])
        data['form'].update(self.read(['currency_id'])[0])
        return data

    def _print_report(self, data):
        res = {}
        data = self.pre_print_report(data)
        # data['form'].update(self.read(['period_length'])[0])
        # data['form'].update(self.read(['currency_id'])[0])
        # data['form'].update(self.read(['partner'])[0])

        period_length = data['form']['period_length']
        if period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise UserError(_('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        currency_id = data['form']['currency_id']
        partner = data['form']['partner']

        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
                'currency': currency_id,
                'partner': partner,
                'direction_selection': data['form']['direction_selection'],
                'result_selection': data['form']['result_selection']
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)
        return self.env.ref('currency_balance.action_report_aged_partner_currency_balance').with_context(landscape=True).report_action(self, data=data)