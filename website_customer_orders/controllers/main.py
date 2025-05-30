# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

from odoo import http, _
from odoo.http import request
from odoo.tools import consteq
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

import logging

_logger = logging.getLogger(__name__)


class CustomerOrdersPortal(CustomerPortal):

    @http.route(['/customer/orders', '/customer/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_customer_orders(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        partner = user.partner_id.parent_id
        _logger.info("USER: %s" % user)
        _logger.info("USER: %s" % user.partner_id.commercial_partner_id.name)

        partner_to_query = user.partner_id.commercial_partner_id
        all_orders_data = request.env['sale.order']._get_customer_orders_data(partner_to_query.id)
        pager = portal_pager(
            url="/customer/orders",
            # url_args={'page': page}, # 'page' zaten URL'de, bu satır gereksiz olabilir
            total=len(all_orders_data),  # Toplam öğe sayısı
            page=page,
            step=self._items_per_page  # CustomerPortal'dan gelen sayfa başına öğe sayısı
        )

        offset = pager['offset']
        items_per_page = self._items_per_page  # Daha okunaklı olması için

        # 3. Sadece mevcut sayfaya ait verileri dilimle
        #    orders_data[offset:offset] YERİNE all_orders_data[offset : offset + items_per_page] KULLANILMALI
        current_page_orders = all_orders_data[offset: offset + items_per_page]

        # offset = pager['offset']
        # limit = pager['limit']
        # current_page_orders = orders_data[offset:offset]

        values.update({
            'orders_data': current_page_orders,
            'page_name': 'orders',
            'pager': pager,
            'default_url': '/customer/orders',
        })
        return request.render("website_customer_orders.portal_customer_orders_template", values)