# Part of Odoo. See LICENSE file for full copyright and licensing details.
from markupsafe import Markup
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class PurchaseDownBill(models.TransientModel):
    _inherit = 'purchase.order.advance.payment'

    # def _prepare_invoice_values(self, order, name, amount, so_line):
    #     invoice_vals = super()._prepare_invoice_values(order, name, amount, so_line)
    #     invoice_vals.update({
    #         'invoice_line_ids': [(0, 0, {
    #             'name': name,
    #             'price_unit': amount,
    #             'quantity': 1.0,
    #             'product_id': self.product_id.id,
    #             'purchase_line_id': so_line.id,
    #             'product_uom_id': so_line.product_uom.id,
    #             'manual_foreign_currency_rate': order.foreign_currency_rate if order.foreign_currency_rate > 0.00 else 0.00,
    #         })],
    #     })
    #
    #     return invoice_vals


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    manual_foreign_currency_rate = fields.Float('Manual Currency Rate')

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
        '''
        print('Hit This Function')
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1

        amount_currency = price_subtotal * sign
        if self.purchase_line_id.order_id.foreign_currency_rate > 0.00:
            balance = amount_currency * self.purchase_line_id.order_id.foreign_currency_rate
        else:
            balance = currency._convert(amount_currency, company.currency_id, company,
                                    date or fields.Date.context_today(self))
        return {
            'amount_currency': amount_currency,
            'currency_id': currency.id,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
        }
