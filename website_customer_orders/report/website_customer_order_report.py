# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

from odoo import models, fields, tools, api, exceptions, _
from requests.auth import HTTPBasicAuth
from odoo.exceptions import UserError
import time, requests
import logging

_logger = logging.getLogger(__name__)


class WebsiteCustomerOrderReport(models.Model):
    _name = "website.customer.order.report"
    _description = "Website Customer Order Report"
    _auto = False
    _rec_name = "order_number"
    _order = "order_number asc"

    id = fields.Integer(string="Id")
    order_number = fields.Char(string="Order Number")
    date_order = fields.Date(string="Date Order")
    confirmation_date = fields.Date(string="Confirmation Date")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    musteri_sip_no = fields.Char(string="Müşteri Sipariş No")
    temsilci = fields.Many2one(comodel_name="res.users", string="Temsilci")
    poz_no = fields.Char(string="Poz No")
    default_code = fields.Char(string="Defualt Code")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    aciklama = fields.Char(string="Açıklama")
    product_uom_qty = fields.Float(string="Product Uom Qty")
    teslim_edilen = fields.Float(string="Teslim Edilen")
    kalan_miktar = fields.Float(string="Kalan Miktar")
    yola_cikis_tarihi = fields.Date(string="Yola Çıkış Tarihi")
    ongorulen_teslim_tarihi = fields.Date(string="ongorulen_teslim_tarihi")
    po_number = fields.Char(string="PO Number")


    _depends = {
        'sale.order': [
            'id', 'name', 'date_order', 'confirmation_date', 'partner_id', 'client_order_ref', 'user_id'
        ],
        'sale.order.line': [
            'order_id', 'name', 'product_id', 'product_uom_qty'
        ],
        'stock.move': [
            'sale_line_id', 'location_dest_id'
        ],
        'stock.location': [
            'usage'
        ],
        'product.product': [
            'default_code'
        ]
    }

    #, sol.sequence2 as poz_no
    @api.model
    def _select(self):
        return """
            select
                sol.id as id
                ,so.name as order_number
                ,so.date_order as date_order
                ,so.confirmation_date as confirmation_date
                ,so.partner_id as partner_id
                ,so.client_order_ref as musteri_sip_no
                ,so.user_id as temsilci

                ,pp.default_code as default_code
                ,sol.product_id as product_id
                ,sol.name as aciklama
                ,sol.product_uom_qty as product_uom_qty
                ,coalesce((select sum(case sl.usage when 'internal' then ((-1) * smc.product_uom_qty) when 'customer' then smc.product_uom_qty else 0 end) from stock_move smc join stock_location sl on sl.id = smc.location_dest_id where smc.sale_line_id = sol.id and smc.state = 'done'),0) as teslim_edilen
                ,(sol.product_uom_qty - coalesce((select sum(case sl.usage when 'internal' then ((-1) * smc.product_uom_qty) when 'customer' then smc.product_uom_qty else 0 end) from stock_move smc join stock_location sl on sl.id = smc.location_dest_id where smc.sale_line_id = sol.id and smc.state = 'done'),0)) as kalan_miktar
                ,(select smg.date_expected::DATE from stock_move smcks
                    join stock_move_move_rel smmr on smmr.move_dest_id = smcks.id
                    join stock_move smg on smg.id = smmr.move_orig_id
                    where smg.sale_line_id isnull and smcks.sale_line_id = sol.id and smcks.state not in ('cancel','done') order by smg.date_expected desc limit 1) as yola_cikis_tarihi
                ,(select case so.id when 1266 then (smg.date_expected + INTERVAL '24 day')::DATE    when 1271 then (smg.date_expected + INTERVAL '24 day')::DATE when 973 then (smg.date_expected + INTERVAL '24 day')::DATE when 763 then (smg.date_expected + INTERVAL '24 day')::DATE
                            when 1221 then (smg.date_expected + INTERVAL '24 day')::DATE when 1196 then (smg.date_expected + INTERVAL '24 day')::DATE else (smg.date_expected + INTERVAL '17 day')::DATE end from stock_move smcks
                    join stock_move_move_rel smmr on smmr.move_dest_id = smcks.id
                    join stock_move smg on smg.id = smmr.move_orig_id
                    where smg.sale_line_id isnull and smcks.sale_line_id = sol.id and smcks.state not in ('cancel','done') order by smg.date_expected desc limit 1) as ongorulen_teslim_tarihi
                ,(select smg.origin from stock_move smcks
                    join stock_move_move_rel smmr on smmr.move_dest_id = smcks.id
                    join stock_move smg on smg.id = smmr.move_orig_id
                    where smg.sale_line_id isnull and smcks.sale_line_id = sol.id and smcks.state not in ('cancel','done') order by smg.date_expected desc limit 1) as po_number
        """

    @api.model
    def _from(self):
        return """
            from sale_order_line sol
            join sale_order so on so.id = sol.order_id
            join product_product pp on pp.id = sol.product_id
            join product_template pt on pt.id = pp.product_tmpl_id
        """

    @api.model
    def _where(self):
        return """
        where pt."type" = 'product'  and so.state in ('sale','done','reserved')
            and (sol.product_uom_qty - coalesce((select sum(case sl.usage when 'internal' then ((-1) * smc.product_uom_qty) when 'customer' then smc.product_uom_qty else 0 end) from stock_move smc join stock_location sl on sl.id = smc.location_dest_id where smc.sale_line_id = sol.id and smc.state = 'done'),0))  != 0
            and so.invoice_status != 'invoiced'
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE OR REPLACE VIEW %s as (
            %s
            %s
            %s
            )
        """ % (self._table, self._select(), self._from(), self._where()))