# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class InheritStockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    def write(self, vals):
        res = super(InheritStockLandedCost, self).write(vals)
        if vals.get("lc_number"):
            for item in self.cost_lines:
                item.name = self.lc_number + '-' + item.product_id.name
        return res


class InheritStockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res['name'] = res.cost_id.lc_number + '-' + res.name if res.cost_id.lc_number else res.name
        return res


class InheritAdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    def _create_accounting_entries(self, move, qty_out):
        # TDE CLEANME: product chosen for computation ?
        cost_product = self.cost_line_id.product_id
        if not cost_product:
            return False
        accounts = self.product_id.product_tmpl_id.get_product_accounts()
        debit_account_id = accounts.get('stock_valuation') and accounts['stock_valuation'].id or False
        # If the stock move is dropshipped move we need to get the cost account instead the stock valuation account
        if self.move_id._is_dropshipped():
            debit_account_id = accounts.get('expense') and accounts['expense'].id or False
        already_out_account_id = accounts['stock_output'].id
        credit_account_id = self.cost_line_id.account_id.id or cost_product.categ_id.property_stock_account_input_categ_id.id
        analytic_account_id = self.cost_line_id.cost_id.analytic_account_id.id or False

        if not credit_account_id:
            raise UserError(_('Please configure Stock Expense Account for product: %s.') % (cost_product.name))

        return self._create_account_move_line(move, analytic_account_id, credit_account_id, debit_account_id, qty_out, already_out_account_id)

    def _create_account_move_line(self, move, analytic_account_id, credit_account_id, debit_account_id, qty_out, already_out_account_id):
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should create the out moves
        """
        AccountMoveLine = []

        base_line = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': 0,
            'analytic_account_id': analytic_account_id
        }
        debit_line = dict(base_line, account_id=debit_account_id)
        credit_line = dict(base_line, account_id=credit_account_id)
        diff = self.additional_landed_cost
        if diff > 0:
            debit_line['debit'] = diff
            credit_line['credit'] = diff
        else:
            # negative cost, reverse the entry
            debit_line['credit'] = -diff
            credit_line['debit'] = -diff
        AccountMoveLine.append([0, 0, debit_line])
        AccountMoveLine.append([0, 0, credit_line])

        # Create account move lines for quants already out of stock
        if qty_out > 0:
            debit_line = dict(base_line,
                              name=(self.name + ": " + str(qty_out) + _(' already out')),
                              quantity=0,
                              account_id=already_out_account_id)
            credit_line = dict(base_line,
                               name=(self.name + ": " + str(qty_out) + _(' already out')),
                               quantity=0,
                               account_id=debit_account_id)
            diff = diff * qty_out / self.quantity
            if diff > 0:
                debit_line['debit'] = diff
                credit_line['credit'] = diff
            else:
                # negative cost, reverse the entry
                debit_line['credit'] = -diff
                credit_line['debit'] = -diff
            AccountMoveLine.append([0, 0, debit_line])
            AccountMoveLine.append([0, 0, credit_line])

            if self.env.company.anglo_saxon_accounting:
                expense_account_id = self.product_id.product_tmpl_id.get_product_accounts()['expense'].id
                debit_line = dict(base_line,
                                  name=(self.name + ": " + str(qty_out) + _(' already out')),
                                  quantity=0,
                                  account_id=expense_account_id)
                credit_line = dict(base_line,
                                   name=(self.name + ": " + str(qty_out) + _(' already out')),
                                   quantity=0,
                                   account_id=already_out_account_id)

                if diff > 0:
                    debit_line['debit'] = diff
                    credit_line['credit'] = diff
                else:
                    # negative cost, reverse the entry
                    debit_line['credit'] = -diff
                    credit_line['debit'] = -diff
                AccountMoveLine.append([0, 0, debit_line])
                AccountMoveLine.append([0, 0, credit_line])

        return AccountMoveLine
