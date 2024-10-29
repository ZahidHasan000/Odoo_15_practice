# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_round, float_compare, OrderedSet

import logging


class StockAccountMove(models.Model):
    _inherit = 'stock.move'

    # def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, svl_id, description):
    #     """
    #     Generate the account.move.line values to post to track the stock valuation difference due to the
    #     processing of the given quant.
    #     """
    #     self.ensure_one()
    #
    #     print("COST:", cost)
    #
    #     # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
    #     # the company currency... so we need to use round() before creating the accounting entries.
    #
    #     if self.purchase_line_id.order_id.import_lc:
    #         unit_price = self.purchase_line_id.price_unit
    #         quantity = self.purchase_line_id.product_qty
    #         custom_currency_rate = self.purchase_line_id.order_id.import_lc.shipping_currency_rate
    #         custom_cost = unit_price * custom_currency_rate
    #         total_cost = custom_cost * quantity
    #         debit_value = self.company_id.currency_id.round(total_cost)
    #         credit_value = debit_value
    #
    #         valuation_partner_id = self._get_partner_id_for_valuation_lines()
    #         res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description).values()]
    #
    #         return res
    #     else:
    #         debit_value = self.company_id.currency_id.round(cost)
    #         credit_value = debit_value
    #
    #         valuation_partner_id = self._get_partner_id_for_valuation_lines()
    #         res = [(0, 0, line_vals) for line_vals in
    #                self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value,
    #                                                    debit_account_id, credit_account_id, svl_id,
    #                                                    description).values()]
    #
    #         return res

    # def _get_in_svl_vals(self, forced_quantity):
    #     svl_vals_list = []
    #     for move in self:
    #         move = move.with_company(move.company_id)
    #         valued_move_lines = move._get_in_move_lines()
    #         valued_quantity = 0
    #         for valued_move_line in valued_move_lines:
    #             valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity, move.product_id.uom_id)
    #
    #         if move.purchase_line_id.order_id.import_lc:
    #             po_line_price_unit = move.purchase_line_id.price_unit
    #             custom_currency_rate = move.purchase_line_id.order_id.import_lc.shipping_currency_rate
    #             # unit_cost = move.product_id.standard_price
    #             unit_cost = po_line_price_unit * custom_currency_rate
    #
    #         else:
    #             unit_cost = move.product_id.standard_price
    #             if move.product_id.cost_method != 'standard':
    #                 unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
    #
    #         svl_vals = move.product_id._prepare_in_svl_vals(forced_quantity or valued_quantity, unit_cost)
    #         svl_vals.update(move._prepare_common_svl_vals())
    #         if forced_quantity:
    #             svl_vals['description'] = 'Correction of %s (modification of past move)' % (move.picking_id.name or move.name)
    #         svl_vals_list.append(svl_vals)
    #     return svl_vals_list


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lc_number = fields.Many2one('lc.management', string="LC")

    # @api.depends('currency_id', 'company_id', 'move_id.date')
    # def _compute_currency_rate(self):
    #     for line in self:
    #         if line.currency_id:
    #             if not line.lc_number:
    #                 line.currency_rate = self.env['res.currency']._get_conversion_rate(
    #                     from_currency=line.company_currency_id,
    #                     to_currency=line.currency_id,
    #                     company=line.company_id,
    #                     date=line.move_id.invoice_date or line.move_id.date or fields.Date.context_today(line),
    #                 )
    #             else:
    #                 line.currency_rate = line.lc_number.shipping_currency_rate
    #         else:
    #             line.currency_rate = 1
