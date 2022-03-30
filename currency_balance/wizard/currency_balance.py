# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api,_
from odoo.exceptions import UserError


class AccountAgedTrialCurrencyBalance(models.TransientModel):

    _name = 'account.aged.trial.currency.balance'
    _inherit = 'account.common.partner.report'
    _description = 'Account Aged Trial Currency Balance Report'

    @api.model
    def _default_currency(self):
        return self.env['res.currency'].search([('name', '=', 'EUR')])

    period_length = fields.Integer(string='Period Length (days)', required=True, default=30)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True)
    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    currency_id = fields.Many2one('res.currency', 'Currency', default=_default_currency, domain=[('name', '!=', 'TRY')])
    direction_selection = fields.Selection([('past', 'Past'), ('future', 'Future')], "Direction Selection", defualt='past')
    partner = fields.Many2one('res.partner', 'Partner')

    def _print_report(self, data):
        # partner = data['form']['partner']
        # raise UserError(partner)
        # raise UserError(data.get('form').get('partner'))
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
        partner = data['form']['partner']

        for i in range(5)[::-1]:
            # if data['form']['direction_selection'] == 'past':
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
                'currency': currency_id,
                'partner': partner
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


