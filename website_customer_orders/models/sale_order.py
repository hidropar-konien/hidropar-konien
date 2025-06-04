# -*- coding: utf-8 -*-
# Copyright 2025 Konien Ltd.Şti.

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

#                 --,sol.sequence2 as poz_no
    @api.model
    def _get_customer_orders_data(self, partner_id):
        """
        Given SQL query is executed to fetch customer's specific order line data.
        :param partner_id: The ID of the customer (res.partner).
        :return: A list of dictionaries, each representing a row from the SQL query.
        """
        query = """
            select
                sol.id as id
                ,so.name as order_number
                ,so.date_order as date_order
                ,so.confirmation_date as confirmation_date
                ,so.partner_id as partner_id
                ,so.client_order_ref as musteri_sip_no
                ,so.user_id as temsilci
                ,sol.sequence2 as poz_no
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
            from sale_order_line sol
            join sale_order so on so.id = sol.order_id
            join product_product pp on pp.id = sol.product_id
            join product_template pt on pt.id = pp.product_tmpl_id
            where pt."type" = 'product'  and so.state in ('sale','done','reserved')

            and (sol.product_uom_qty - coalesce((select sum(case sl.usage when 'internal' then ((-1) * smc.product_uom_qty) when 'customer' then smc.product_uom_qty else 0 end) from stock_move smc join stock_location sl on sl.id = smc.location_dest_id where smc.sale_line_id = sol.id and smc.state = 'done'),0))  != 0
            and so.invoice_status != 'invoiced'
        """
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        return result

#             and so.partner_id = %s  self.env.cr.execute(query, (partner_id,))

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
class ProductProduct(models.Model):
    _inherit = "product.product"
class ProductTemplate(models.Model):
    _inherit = "product.template"
class StockMove(models.Model):
    _inherit = "stock.move"
class StockLocation(models.Model):
    _inherit = "stock.location"