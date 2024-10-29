# -*- coding: utf-8 -*-
from lxml import etree
from collections import defaultdict
from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    inv_bill_id = fields.Many2one('account.move', string="INV/BILL ID")
    inv_bill_ids = fields.Many2many('account.move', string="Move IDS")
    payee_name = fields.Char('Payee Name')

    def action_post(self):
        for rec in self:
            print(rec.state)
            if rec.state != 'signed' and rec.payment_type == 'outbound':
                raise UserError(
                    _('You are not Allowed to confirm Unsigned Payment, Please make sure the payment are signed. Payment No: %s') % (
                        rec.name))
            else:
                res = super().action_post()
                rec.custom_reconcile_payment()
                rec.proceed_payment_bill()
                return res

    def add_payment(self):
        # if self.inv_bill_id:
        domain = [
            ('parent_state', '=', 'posted'),
            ('account_internal_type', 'in', ('receivable', 'payable')),
            ('reconciled', '=', False),
        ]
        payment_lines = self.line_ids.filtered_domain(domain)
        if self.inv_bill_id:
            line_id = payment_lines.id
            self.inv_bill_id.js_assign_outstanding_line(line_id)
        elif self.inv_bill_ids:
            line_ids = payment_lines.id
            for item in self.inv_bill_ids:
                item.js_assign_outstanding_line(line_ids)

    def _reconcile_payments(self, to_process):
        domain = [
            ('parent_state', '=', 'posted'),
            ('account_internal_type', 'in', ('receivable', 'payable')),
            ('reconciled', '=', False),
        ]
        for vals in to_process:

            payment_lines = self.line_ids.filtered_domain(domain)
            lines = vals['to_reconcile']

            for account in payment_lines.account_id:
                # print('joyanto joyanto', payment_lines)
                # print('joyanto2 joyanto2', lines)
                (payment_lines + lines) \
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]) \
                    .reconcile()

    def custom_reconcile_payment(self):
        if self.inv_bill_id:
            move_id = self.inv_bill_id.id
            batches = self._get_batches(move_id)
            to_process = []
            if batches:
                to_process.append({
                    'to_reconcile': batches[0]['lines'],
                    'batch': batches[0],
                })
            self._reconcile_payments(to_process)

        elif self.inv_bill_ids:
            for item in self.inv_bill_ids:
                move_id = item.id
                batches = self._get_batches(move_id)
                to_process = []
                if batches:
                    to_process.append({
                        'to_reconcile': batches[0]['lines'],
                        'batch': batches[0],
                    })
                self._reconcile_payments(to_process)
        else:
            pass

    @api.model
    def _get_line_batch_key(self, line):
        ''' Turn the line passed as parameter to a dictionary defining on which way the lines
        will be grouped together.
        :return: A python dictionary.
        '''
        move = line.move_id

        partner_bank_account = self.env['res.partner.bank']
        if move.is_invoice(include_receipts=True):
            partner_bank_account = move.partner_bank_id._origin

        return {
            'partner_id': line.partner_id.id,
            'account_id': line.account_id.id,
            'currency_id': line.currency_id.id,
            'partner_bank_id': partner_bank_account.id,
            'partner_type': 'customer' if line.account_internal_type == 'receivable' else 'supplier',
        }
    #
    def _get_batches(self, move_id):
        ''' Group the account.move.line linked to the wizard together.
        Lines are grouped if they share 'partner_id','account_id','currency_id' & 'partner_type' and if
        0 or 1 partner_bank_id can be determined for the group.
        :return: A list of batches, each one containing:
            * payment_values:   A dictionary of payment values.
            * moves:        An account.move recordset.
        '''
        self.ensure_one()
        domain = [
            ('parent_state', '=', 'posted'),
            ('account_internal_type', 'in', ('receivable', 'payable')),
            ('reconciled', '=', False),
        ]
        get_move = self.env['account.move'].sudo().search([('id', '=', move_id)])
        lines = get_move.line_ids.filtered_domain(domain)

        if len(lines.company_id) > 1:
            raise UserError(_("You can't create payments for entries belonging to different companies."))
        if not lines:
            raise UserError(_("You can't open the register payment wizard without at least one receivable/payable line."))

        batches = defaultdict(lambda: {'lines': self.env['account.move.line']})
        for line in lines:
            print('######', line.id)
            batch_key = self._get_line_batch_key(line)
            serialized_key = '-'.join(str(v) for v in batch_key.values())
            vals = batches[serialized_key]
            vals['payment_values'] = batch_key
            vals['lines'] += line

        # Compute 'payment_type'.
        for vals in batches.values():
            lines = vals['lines']
            balance = sum(lines.mapped('balance'))
            vals['payment_values']['payment_type'] = 'inbound' if balance > 0.0 else 'outbound'

        return list(batches.values())

    def proceed_payment_bill(self):
        if self.payment_type == 'outbound':
            for item in self.inv_bill_ids:
                item.proceed_for_payment = False

        else:
            pass
