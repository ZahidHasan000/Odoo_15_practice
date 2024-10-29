# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SOFixDiscount(models.Model):
    _inherit="sale.order"
    
    # def _prepare_invoice(self):
    #     invoice_vals = super(SOFixDiscount, self)._prepare_invoice()
    #     invoice_line_vals = []
    #     for line in self.order_line:
    #         invoice_line_vals.append((0, 0, line.prepare_invoice_line_vals()))
    #     invoice_vals['invoice_line_ids'] = invoice_line_vals
    #     return invoice_vals
    
    # def _prepare_invoice(self):
    #     invoice_vals = super(SOFixDiscount, self)._prepare_invoice()
    #     invoice_line_vals = []
    #     for line in self.order_line:
    #         invoice_line_vals.append((0, 0, {
    #             'fix_discount': line.fix_discount,
    #             'ref': line.order_id.client_order_ref,
    #             'move_type': 'out_invoice',
    #             'invoice_origin': line.order_id.name,
    #             'invoice_user_id': line.order_id.user_id.id,
    #             'narration': line.order_id.note,
    #             'partner_id': line.order_id.partner_invoice_id.id,
    #             'fiscal_position_id': (line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(line.order_id.partner_id.id)).id,
    #             'partner_shipping_id': line.order_id.partner_shipping_id.id,
    #             'currency_id': line.order_id.pricelist_id.currency_id.id,
    #             'payment_reference': line.order_id.reference,
    #             'invoice_payment_term_id': line.order_id.payment_term_id.id,
    #             'partner_bank_id': line.order_id.company_id.partner_id.bank_ids[:1].id,
    #             'team_id': line.order_id.team_id.id,
    #             'campaign_id': line.order_id.campaign_id.id,
    #             'medium_id': line.order_id.medium_id.id,
    #             'source_id': line.order_id.source_id.id,
    #             'invoice_line_ids': [(0, 0, {
    #                 'name': name,
    #                 'price_unit': amount,
    #                 'quantity': 1.0,
    #                 'product_id': self.product_id.id,
    #                 'product_uom_id': so_line.product_uom.id,
    #                 'tax_ids': [(6, 0, so_line.tax_id.ids)],
    #                 'sale_line_ids': [(6, 0, [so_line.id])],
    #                 'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
    #                 'analytic_account_id': order.analytic_account_id.id if not so_line.display_type and order.analytic_account_id.id else False,
    #             })],
    #         }))
    #     invoice_vals['invoice_line_ids'] = invoice_line_vals
    #     return invoice_vals
    
class SaleOrderLine(models.Model):
    _inherit="sale.order.line"
    
    # disc = fields.Float(string='Disc%')
    # def prepare_invoice_line_vals(self):
    #     return {
    #         'fix_discount': self.fix_discount,            
    #     }