# -*- coding: utf-8 -*-
# Copyright 2020 Konien Ltd.Şti.


from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportAgedPartnerBalance(models.AbstractModel):
    _inherit = 'report.account.report_agedpartnerbalance'


    def _get_partner_currency_move_lines(self, account_type, date_from, target_move, currency_id, period_length,
                                       direction_selection='Past', partner_id=False):
        periods = {}
        start = datetime.strptime(date_from, "%Y-%m-%d")
        if direction_selection == 'Past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                period_name = str((5 - (i + 1)) * period_length + 1) + '-' + str((5 - i) * period_length)
                period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
                if i == 0:
                    period_name = '+' + str(4 * period_length)
                periods[str(i)] = {
                    'name': period_name,
                    'stop': period_stop,
                    'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                periods[str(5 - (i + 1))] = {
                    'name': (i != 4 and str((i) * period_length) + '-' + str((i + 1) * period_length) or (
                            '+' + str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i != 4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)

        res = []
        total = []
        cr = self.env.cr
        user_company = self.env.user.company_id
        # user_currency = user_company.currency_id
        user_currency = user_company.currency_id
        select_currency = self.env['res.currency'].browse(currency_id[0])
        # res_currency = self.env['res.currency'].with_context(date=date_from)




        company_ids = self._context.get('company_ids') or [user_company.id]
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type),
                    date_from, date_from, date_from, tuple(company_ids))

        partner_filter = ''
        if partner_id:
            partner_filter = ' AND l.partner_id = %s ' % str(partner_id[0])

        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND (
                        l.reconciled IS FALSE
                        OR l.id IN(
                            SELECT credit_move_id FROM account_partial_reconcile where max_date > %s
                            UNION ALL
                            SELECT debit_move_id FROM account_partial_reconcile where max_date > %s
                        )
                    )
                AND (l.date <= %s)
                AND l.company_id IN %s  ''' + partner_filter + '''
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        for i in range(7):
            total.append(0)
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}
        undue_amounts = {}
        if direction_selection == 'Past':
            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND (COALESCE(l.date_maturity,l.date) >= %s)\
                        AND ((l.partner_id IN %s) )
                    AND (l.date <= %s)
                    AND l.company_id IN %s'''
        else:
            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND (COALESCE(l.date_maturity,l.date) <= %s)\
                        AND ((l.partner_id IN %s) )
                    AND (l.date <= %s)
                    AND l.company_id IN %s'''
        cr.execute(query, (
            tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, tuple(company_ids)))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            # line_amount = res_currency._compute(line.company_id.currency_id, user_currency, line.balance)
            line_amount = self.env['res.currency'].with_context(
                {
                    'currency_rate_type_from': line.partner_id.customer_currency_rate_type_id,
                    'currency_rate_type_to': line.partner_id.customer_currency_rate_type_id,
                    'date': line.date
                })._compute(line.company_id.currency_id, select_currency, line.balance)
            if user_currency.is_zero(line_amount):
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.max_date <= date_from:
                    # line_amount += res_currency._compute(partial_line.company_id.currency_id, user_currency,
                    #                                     partial_line.amount)
                    line_amount += self.env['res.currency'].with_context(
                        {
                            'currency_rate_type_from': line.partner_id.customer_currency_rate_type_id,
                            'currency_rate_type_to': line.partner_id.customer_currency_rate_type_id,
                            'date': line.date
                        })._compute(line.company_id.currency_id, select_currency, line.amount)

            for partial_line in line.matched_credit_ids:
                if partial_line.max_date <= date_from:
                    # line_amount -= res_currency._compute(partial_line.company_id.currency_id, user_currency,
                    #                                     partial_line.amount)
                    line_amount -= self.env['res.currency'].with_context(
                        {
                            'currency_rate_type_from': line.partner_id.customer_currency_rate_type_id,
                            'currency_rate_type_to': line.partner_id.customer_currency_rate_type_id,
                            'date': line.date
                        })._compute(line.company_id.currency_id, select_currency, line.amount)

            if not self.env.user.company_id.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) )
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids).with_context(prefetch_fields=False):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                # line_amount = res_currency._compute(line.company_id.currency_id, user_currency, line.balance)
                line_amount = self.env['res.currency'].with_context(
                    {
                        'currency_rate_type_from': line.partner_id.customer_currency_rate_type_id,
                        'currency_rate_type_to': line.partner_id.customer_currency_rate_type_id,
                        'date': line.date
                    })._compute(line.company_id.currency_id, select_currency, line.balance)
                if user_currency.is_zero(line_amount):
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        # line_amount += res_currency._compute(partial_line.company_id.currency_id, user_currency,
                        #                                     partial_line.amount)
                        line_amount += self.env['res.currency'].with_context(
                            {
                                'currency_rate_type_from': line.partner_id.customer_currency_rate_type_id,
                                'currency_rate_type_to': line.partner_id.customer_currency_rate_type_id,
                                'date': line.date
                            })._compute(line.company_id.currency_id, select_currency, line.amount)
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        # line_amount -= res_currency._compute(partial_line.company_id.currency_id, user_currency,
                        #                                     partial_line.amount)
                        line_amount -= self.env['res.currency'].with_context(
                            {
                                'currency_rate_type_from': line.partner_id.customer_currency_rate_type_id,
                                'currency_rate_type_to': line.partner_id.customer_currency_rate_type_id,
                                'date': line.date
                            })._compute(line.company_id.currency_id, select_currency, line.amount)

                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                    })
            history.append(partners_amount)

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[
                                                                                  0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
                res.append(values)

        return res, total, lines

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']
        currency_id = data['form']['currency_id']
        period_length = data['form']['period_length']
        direction_selection = data['form']['direction_selection']
        partner_id = data['form']['partner_id']
        movelines, total, dummy = self._get_partner_currency_move_lines(account_type, date_from, target_move,
                                                                        currency_id, period_length, direction_selection,
                                                                        partner_id)
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_partner_lines': movelines,
            'get_direction': total,
        }
