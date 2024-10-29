# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Aswathi PN (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
##############################################################################
from odoo import api, models, fields, _
from odoo.tools import float_is_zero
from itertools import groupby
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    """
        This class is created for inherited model Purchase Order.

        Methods:
            _nothing_to_invoice_error(self):
                Function for showing the user error while there is no products are received for the purchase order.

            _deduct_payment(self):
                This function is for deducting the down payment amount from next down payment invoice.

            _prepare_down_payment_section_line(self):
                Function for creating dict of values to create a new purchase down payment section.

            _get_invoiceable_lines(self):
                Function for returning the orders invoiceable lines.

        """
    _inherit = 'purchase.order'

    @api.model
    def _nothing_to_invoice_error(self):
        """Function to showing user error while there is no products are received for the purchase order"""
        return UserError(_(
            "There is nothing to bill!\n\n"
            "Reason(s) of this behavior could be:\n"
            "- You should receive your products before billing them: Click on the \"truck\" icon "
            "(top-right of your screen) and follow instructions.\n"
            "- You should modify the control policy of your product: Open the product, go to the "
            "\"Purchase\" tab and modify control policy from \"On received quantities\" to \"On ordered "
            "quantities\"."
        ))

    def _deduct_payment(self, grouped=False, final=False, date=None):
        """
        Create the Bill associated to the PO.
        :returns: list of created invoices
        """
        invoice_vals_list = []
        invoice_item_sequence = 0  # Incremental sequencing to keep the lines order on the invoice.
        for order in self:
            order = order.with_company(order.company_id)
            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)
            if not any(not line.display_type for line in invoiceable_lines):
                continue
            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                # Editing Here
                # if not down_payment_section_added and line.is_downpayment:
                #     invoice_line_vals.append(
                #         (0, 0, order._prepare_down_payment_section_line(
                #             sequence=invoice_item_sequence,
                #         )),
                #     )
                #     down_payment_section_added = True
                #     invoice_item_sequence += 1
                invoice_line_vals.append(
                    (0, 0, line._prepare_invoice_line(
                        sequence=invoice_item_sequence,
                    )),
                )
                invoice_item_sequence += 1
            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)
        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [
                    x.get(grouping_key) for grouping_key in invoice_grouping_keys
                ]
            )
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list
        if len(invoice_vals_list) < len(self):
            PurchaseOrderLine = self.env['purchase.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = PurchaseOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        return moves

    @api.model
    def _prepare_down_payment_section_line(self, **optional_values):
        """
        Prepare the dict of values to create a new down payment section for a purchase order line.
        :param optional_values: any parameter that should be added to the returned down payment section
        """
        context = {'lang': self.partner_id.lang}
        down_payments_section_line = {
            'display_type': 'line_section',
            'name': _('Down Payments'),
            'product_id': False,
            'product_uom_id': False,
            'quantity': 0,
            'discount': 0,
            'price_unit': 0,
            'account_id': False
        }
        del context
        if optional_values:
            down_payments_section_line.update(optional_values)
        return down_payments_section_line

    def _get_invoice_grouping_keys(self):
        """Function to return the invoice grouping keys"""
        return ['company_id', 'partner_id', 'currency_id']

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self.order_line:
            if line.display_type == 'line_section':
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)
        # Editing Here
        # return self.env['purchase.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)
        return self.env['purchase.order.line'].browse(invoiceable_line_ids)

    def get_purchase_total_invoices_amount(self):
        for purchase in self:
            payment = 0
            if purchase.invoice_ids:
                for bill in purchase.invoice_ids:
                    payment += bill.amount_total
            purchase.total_invoices_amount = payment

    def hide_create_bill_status(self):
        for purchase in self:
            if purchase.total_invoices_amount >= purchase.amount_total:
                purchase.hide_create_bill = False
            else:
                purchase.hide_create_bill = False

    total_invoices_amount = fields.Float(string='Advance Payment Amount', compute='get_purchase_total_invoices_amount')
    hide_create_bill = fields.Boolean(string='Hide Create Bill', copy=False, compute='hide_create_bill_status')

    def action_create_invoice(self):
        """Create the invoice associated to the PO and Update the invoice-able
         lines on the basis of selected lines"""
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            if order.invoice_status != 'to invoice':
                continue
            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if ((line.is_product_select is True) or True not in
                        order.order_line.mapped('is_product_select')):
                    if line.display_type == 'line_section':
                        pending_section = line
                        continue
                    if not float_is_zero(line.qty_to_invoice,
                                         precision_digits=precision):
                        if pending_section:
                            line_vals = (
                                pending_section._prepare_account_move_line())
                            line_vals.update({'sequence': sequence})
                            invoice_vals['invoice_line_ids'].append(
                                (0, 0, line_vals))
                            sequence += 1
                            pending_section = None
                        line_vals = line._prepare_account_move_line()
                        line_vals.update({'sequence': sequence})
                        invoice_vals['invoice_line_ids'].append(
                            (0, 0, line_vals))
                        sequence += 1
                # else:
                #     line.is_product_select = True
            invoice_vals_list.append(invoice_vals)
        if not invoice_vals_list:
            raise UserError(_('There is no invoice-able line. If a product has'
                              ' a control policy based on received quantity, '
                              'please make sure that a quantity has '
                              'been received.'))
        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list,
                                               key=lambda x: (
                                                       x.get('company_id'),
                                                       x.get('partner_id'),
                                                       x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += \
                        invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.
                pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list
        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(
            default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
        # 4) Some moves might actually be refunds: convert them if the
        # total amount is negative
        # We do this after the moves have been created since we need taxes,
        # 'etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0) \
            .action_switch_invoice_into_refund_credit_note()
        return self.action_view_invoice(moves)


class AccountMoveDownPayment(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()
        for rec in self:
            # print('HIt the action post')
            if rec.advance_bill_status == 'advance_bill' and rec.move_type == 'in_invoice':
                for item in rec.invoice_line_ids:
                    item.purchase_line_id.is_product_select = True

        return res

    def button_draft(self):
        res = super().button_draft()
        for rec in self:
            # print('HIt the action post')
            if rec.advance_bill_status == 'advance_bill' and rec.move_type == 'in_invoice':
                for item in rec.invoice_line_ids:
                    item.purchase_line_id.is_product_select = False

        return res