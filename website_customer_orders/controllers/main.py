# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)


class CustomerOrdersPortal(CustomerPortal):

    @http.route(['/customer/orders', '/customer/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_customer_orders(self, page=1, **kw):
        user = http.request.env.user
        partner = user.partner_id

        orders_data = http.request.env['sale.order']._get_customer_orders_data(partner.id)

        pager = http.request.website.pager(
            url="/customer/orders",
            total=len(orders_data),
            page=page,
            step=10
        )

        offset = pager['offset']
        # limit = pager['limit']
        current_page_orders = orders_data[offset:offset]

        values = {
            'orders_data': current_page_orders,
            'page_name': 'orders',
            'pager': pager,
        }
        return http.request.render("website_customer_orders.portal_customer_orders_template", values)