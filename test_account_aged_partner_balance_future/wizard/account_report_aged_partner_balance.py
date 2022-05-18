import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountAgedTrialBalance(models.TransientModel):
    _inherit = 'account.aged.trial.balance'

    partner_id = fields.Many2one('res.partner', 'Partner')

    direction_selection = fields.Selection([('past', 'Past'), ('future', 'Future')],
                                           'Analysis Direction',
                                           required=True, default='past')
    @api.multi
    def pre_print_report(self, data):
        data = super(AccountAgedTrialBalance, self).pre_print_report(data)
        data['form'].update(self.read(['direction_selection'])[0])
        data['form'].update(self.read(['partner_id'])[0])
        return data

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

        if data['form']['direction_selection'] == 'past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length - 1)
                res[str(i)] = {
                    'name': (i != 0 and (str((5 - (i + 1)) * period_length) + '-' + str((5 - i) * period_length)) or (
                            '+' + str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                res[str(5-(i+1))] = {
                    'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)

        data['form'].update(res)

        return self.env.ref('account.action_report_aged_partner_balance').with_context(landscape=True).report_action(
            self, data=data)
