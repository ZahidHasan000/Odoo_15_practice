# Part of Odoo. See LICENSE file for full copyright and licensing details.
from markupsafe import Markup
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class PurchaseOrderLC(models.Model):
    _inherit = 'purchase.order'

    foreign_currency_rate = fields.Float('Foreign Currency Rate')

    def button_confirm(self):
        res = super().button_confirm()
        if self.po_sourcing_type == 'foreign' and self.foreign_currency_rate <= 0.00:
            raise UserError(_('Please Set The Foreign Currency Rate Greater Than 0.00'))
        else:
            return res
        
    # def action_create_invoice(self):
    #     for rec in self:
    #         print('hit create invoice')
    #         for line in rec.order_line:
    #             line_vals = line._prepare_account_move_line()
    #             line_vals.update({'manual_foreign_currency_rate': rec.foreign_currency_rate if rec.foreign_currency_rate > 0.00 else 0.00})
    #
    #     return super().action_create_invoice()


class PurchaseOrderLineLC(models.Model):
    _inherit = 'purchase.order.line'

    def _get_stock_move_price_unit(self):
        self.ensure_one()
        print("HIT Custom Function _get_stock_move_price_unit")
        order = self.order_id
        price_unit = self.price_unit
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
        if self.taxes_id:
            qty = self.product_qty or 1
            price_unit = self.taxes_id.with_context(round=False).compute_all(
                price_unit, currency=self.order_id.currency_id, quantity=qty, product=self.product_id, partner=self.order_id.partner_id
            )['total_void']
            price_unit = float_round(price_unit / qty, precision_digits=price_unit_prec)
        if self.product_uom.id != self.product_id.uom_id.id:
            price_unit *= self.product_uom.factor / self.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            if order.po_sourcing_type == 'foreign' and order.foreign_currency_rate > 0.00:
                price_unit = price_unit * order.foreign_currency_rate
                print('price_unit', price_unit)
            else:
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, self.company_id, self.date_order or fields.Date.today(), round=False)
        return price_unit

    # def _prepare_account_move_line(self, move=False):
    #     res = super()._prepare_account_move_line(move)
    #     res.update({'manual_foreign_currency_rate': self.order_id.foreign_currency_rate if self.order_id.foreign_currency_rate > 0.00 else 0.00})
    #     return res


class PurchaseStock(models.Model):
    _inherit = 'stock.move'

    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
            line = self.purchase_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                qty = line.product_qty or 1
                price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=qty)['total_void']
                price_unit = float_round(price_unit / qty, precision_digits=price_unit_prec)
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                # The date must be today, and not the date of the move since the move move is still
                # in assigned state. However, the move date is the scheduled date until move is
                # done, then date of actual move processing. See:
                # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
                if order.po_sourcing_type == 'foreign' and order.foreign_currency_rate > 0.00:
                    price_unit = price_unit * order.foreign_currency_rate
                else:
                    price_unit = order.currency_id._convert(
                        price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)

            return price_unit

        return super(PurchaseStock, self)._get_price_unit()
