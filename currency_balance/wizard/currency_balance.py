# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
<<<<<<< HEAD
from odoo import fields, models, api, _
=======
from odoo import fields, models, _
>>>>>>> parent of eab8151... [UPD] - default verrency add
from odoo.exceptions import UserError


class AccountAgedTrialCurrencyBalance(models.TransientModel):

    _name = 'konien.account.aged.trial.currency.balance'
    _inherit = 'account.common.partner.report'
    _description = 'Account Aged Trial Currency Balance Report'

    period_length = fields.Integer(string='Period Length (days)', required=True, default=30)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True)
    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    currency_id = fields.Many2one('res.currency', 'Currency')
    direction_selection = fields.Selection([('past', 'Past'), ('future', 'Future')], "Direction Selection", defualt='past')
    partner = fields.Many2one('res.partner', 'Partner')

<<<<<<< HEAD
    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', []),
                'model': self.env.context.get('active_model', 'ir.ui.menu'),
                'form': self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'currency_id', 'partner', 'direction_selection', 'result_selection'])[0]}
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self._print_report(data)

    def pre_print_report(self, data):
        data['form'].update(self.read(['result_selection'])[0])
        data['form'].update(self.read(['partner'])[0])
        data['form'].update(self.read(['direction_selection'])[0])
        data['form'].update(self.read(['currency_id'])[0])
        return data

=======
>>>>>>> parent of eab8151... [UPD] - default verrency add
    def _print_report(self, data):
        res = {}
        data = self.pre_print_report(data)
        data['form'].update(self.read(['period_length'])[0])
        period_length = data['form']['period_length']
        if period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise UserError(_('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        currency_id = data['form']['currency_id']

        for i in range(5)[::-1]:
            # if data['form']['direction_selection'] == 'past':
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
                'currency': currency_id,
                'partner': data['form']['partner']
            }
            start = stop - relativedelta(days=1)
            # elif data['form']['direction_selection'] == 'future':
            #     stop = start + relativedelta(days=period_length - 1)
            #     res[str(i)] = {
            #         'name': (i != 0 and (str((5 - (i + 1)) * period_length) + '-' + str((5 - i) * period_length)) or (
            #                     '+' + str(4 * period_length))),
            #         'stop': start.strftime('%Y-%m-%d'),
            #         'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            #         'currency': currency_id
            #     }
            #     start = stop + relativedelta(days=1)
        data['form'].update(res)
        return self.env.ref('currency_balance.action_report_aged_partner_currency_balance').with_context(landscape=True).report_action(self, data=data)


