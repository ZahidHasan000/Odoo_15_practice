# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, api, _
import time


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        ''' Load from either an old purchase order, either an old vendor bill.

        When setting a 'purchase.bill.union' in 'purchase_vendor_bill_id':
        * If it's a vendor bill, 'invoice_vendor_bill_id' is set and the loading is done by '_onchange_invoice_vendor_bill'.
        * If it's a purchase order, 'purchase_id' is set and this method will load lines.

        /!\ All this not-stored fields must be empty at the end of this function.
        '''
        if self.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elif self.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        self.purchase_vendor_bill_id = False

        if not self.purchase_id:
            return

        # Copy data from PO
        invoice_vals = self.purchase_id.with_company(self.purchase_id.company_id)._prepare_invoice()
        del invoice_vals['ref']
        self.update(invoice_vals)

        # Copy purchase lines.
        po_lines = self.purchase_id.order_line - self.line_ids.mapped('purchase_line_id')
        new_lines = self.env['account.move.line']
        if self.purchase_id.down_payment_by == 'dont_deduct_down_payment':
            list_item2 = []
            for line in po_lines.filtered(lambda l: not l.display_type):
                new_line = new_lines.new(line._prepare_account_move_line(self))
                new_line.account_id = new_line._get_computed_account()
#                if not line.is_down_payment:
#                    new_line.quantity = 1
                new_line._onchange_price_subtotal()
                new_lines += new_line
                list_item2.append((0, 0, line._prepare_account_move_line(self)))
            self.invoice_line_ids = list_item2
            for line_item in self.invoice_line_ids:
                line_item.account_id = line_item._get_computed_account()

        if self.purchase_id.down_payment_by == 'deduct_down_payment':
            print('joyanto', self.purchase_id.name)
            list_item = []
            for line in self.purchase_id.order_line:
                new_line = new_lines.new(line._prepare_account_move_line(self))
                new_line.account_id = new_line._get_computed_account()
#                if not line.is_down_payment:
#                    new_line.quantity = 1
                new_line._onchange_price_subtotal()
                new_lines += new_line
                list_item.append((0, 0, line._prepare_account_move_line(self)))
            self.invoice_line_ids = list_item
            for line_item in self.invoice_line_ids:
                line_item.account_id = line_item._get_computed_account()

        if self.purchase_id.down_payment_by in ['fixed', 'percentage']:
            amount = self.purchase_id.amount
            if self.purchase_id.down_payment_by == 'percentage':
                amount = self.purchase_id.amount_total * self.purchase_id.amount / 100
            po_line_obj = self.env['purchase.order.line']
            product = self.purchase_id.company_id.down_payment_product_id
            if product:
                product_id = self.env['product.product'].browse(int(product))
            po_line = po_line_obj.create({'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                                          'price_unit': amount,
                                          'product_qty': 0.0,
                                          'order_id': self.purchase_id.id,
                                          'product_uom': product_id.uom_id.id,
                                          'product_id': product_id.id,
                                          'date_planned': self.purchase_id.date_order,
                                          'is_down_payment': True
                                          })
            po_line.taxes_id = False
            data = {'product_id': product_id.id or False,
                    'name': _('Advance Payment'),
                    'price_unit': amount,
                    'quantity': 1,
                    'purchase_line_id': po_line.id,
                    'move_id': self.id}
            new_line = new_lines.new(data)
            new_line.quantity = 1
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Compute ref.
        refs = self._get_invoice_reference()
        self.ref = ', '.join(refs)

        # Compute payment_reference.
        if len(refs) == 1:
            self.payment_reference = refs[0]

        self.purchase_id = False
        self._onchange_currency()
        self.partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
