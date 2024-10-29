# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SolBDTPrice(models.Model):
    _inherit = 'sale.order.line'
    
    bdt_subtotal=fields.Float(string="BDT Subtotal",readonly=True,compute="_get_bdt_total")
    
    @api.depends('price_subtotal','order_id.pricelist_id')
    def _get_bdt_total(self):
        for line in self:
            if line.order_id.pricelist_id.currency_id.rate_ids:
                line.update({
                    'bdt_subtotal': (line.price_subtotal)*(line.order_id.pricelist_id.currency_id.rate_ids[0].inverse_company_rate),
                })
            else:
                line.update({
                    'bdt_subtotal': (line.price_subtotal),
                })
    
class InheritSO(models.Model):
    _inherit = 'sale.order'
    
    bdt_amount_total=fields.Float(string="BDT Total",readonly=True,compute="_get_bdt_amount_total",store=True)
    
    @api.depends(
        'amount_total',
        'pricelist_id',
        'pricelist_id.currency_id',
        'pricelist_id.currency_id.rate_ids',
        'pricelist_id.currency_id.rate_ids.inverse_company_rate'
        )
    def _get_bdt_amount_total(self):
        for rec in self:
            if rec.pricelist_id.currency_id.rate_ids:
                rec.bdt_amount_total = (rec.amount_total)*(rec.pricelist_id.currency_id.rate_ids[0].inverse_company_rate)
            else:
                rec.bdt_amount_total = rec.amount_total