# -*- coding: utf-8 -*-
from collections import defaultdict
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, frozendict


class InheritAccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # def get_default_move_id(self):
    #     move_id = self.env['account.move'].browse(self._context.get('active_ids', [])).id
    #
    #     return move_id

    payee_name = fields.Char('Payee Name')

    def get_default_move_batch_ids(self):
        move_ids = self.env['account.move'].browse(self._context.get('active_ids', [])).ids

        return move_ids

    @api.depends('can_edit_wizard')
    def _compute_move_ids(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                move = wizard.env['account.move.line'].browse(wizard._context.get('active_ids', []))
                wizard['inv_bill_ids'] = [(6, 0, move.ids)]
            else:
                wizard['inv_bill_ids'] = False

    inv_bill_ids = fields.Many2many('account.move', string="Move IDS", compute='_compute_move_ids')

    def _create_payment_vals_from_wizard(self):
        vals = super()._create_payment_vals_from_wizard()
        if self.inv_bill_ids:
            vals.update({
                'inv_bill_ids': self.inv_bill_ids,
                'payee_name': self.payee_name,
            })
        return vals

    @api.model
    def _get_batch_get_move_id(self, batch_result):
        ''' Helper to compute the communication based on the batch.
        :param batch_result:    A batch returned by '_get_batches'.
        :return:                A string representing a communication to be set on payment.
        '''

        # for line in batch_result['lines']:
        #     move_id = line.move_id.id
        #     move_name = line.move_id.name
        #     # print('Reference meta', move_name)
        labels = list(line.move_id.id for line in batch_result['lines'])
        return labels

    def _create_payment_vals_from_batch(self, batch_result):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        payment_vals['inv_bill_ids'] = [(6, 0, self._get_batch_get_move_id(batch_result))]
        payment_vals['payee_name'] = self.payee_name
        return payment_vals



