
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta

import json
import requests
# from urllib.parse import urlparse
import urllib.parse


class LcManageShipmentInherit(models.Model):
    _inherit = 'lc.management'
    _order = 'id desc'

    #LC Shipment
    lc_manage_shipment_date = fields.Date('Date')
    lc_manage_shipment_currency = fields.Many2one('res.currency', string='Currency')
    lc_manage_shipment_currency_rate = fields.Float(string='Currency Rate BDT', default=1.00, digits=(16, 12))
    lc_shipment_acceptance_charge = fields.Float(string="LC Documents Acceptance Charge")
    lc_shipment_doc_charge_account = fields.Many2one('account.account', string="Document Charge Account")
    lc_shipment_deferred_interest = fields.Float(string="Interest of Deferred LC")
    lc_shipment_deferred_account = fields.Many2one('account.account', string="Deferred Interest Account")
    lc_shipment_confirmation = fields.Float(string="LC Confirmation")
    lc_shipment_charge_account = fields.Many2one('account.account', string="Confirmation Charge Account")
    lc_shipment_pay_account = fields.Many2one('account.account', string="Payment Account")
    lc_shipment_journal = fields.Many2one('account.move', string="LC Shipment Journal")

    @api.onchange('lc_manage_shipment_currency')
    def get_lc_shipment_currency_rate(self):
        if self.lc_manage_shipment_currency:
            company = self.env.company
            today_date = self.lc_manage_shipment_date if self.lc_manage_shipment_date else fields.Date.today()
            from_currency = self.env.company.currency_id
            to_currency = self.lc_manage_shipment_currency

            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100.00 / rates
            self.lc_manage_shipment_currency_rate = final_rate / 100.00
        else:
            self.lc_manage_shipment_currency_rate = 1.00

    def create_lc_shipment_journal(self):
        for rec in self:
            amount = rec.lc_shipment_acceptance_charge + rec.lc_shipment_deferred_interest + rec.lc_shipment_confirmation
            if rec.lc_shipment_charge_account and rec.lc_shipment_pay_account and not rec.lc_shipment_journal:
                reference = 'LC Shipment For LC ' + str(rec.lc_number)
                # journal_id = rec.env['account.journal'].sudo().search([['name', '=', 'LC Management']], limit=1).id
                journal_id = rec.default_journal.id
                journal = rec.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': reference,
                    'date': rec.lc_manage_shipment_date if rec.lc_manage_shipment_date else fields.Date.today(),
                    'journal_id': journal_id,
                    'currency_id': rec.env.company.currency_id.id
                })

                if journal:
                    vals = {
                        "line_ids": [
                            [0, 0, {
                                "account_id": rec.lc_shipment_doc_charge_account.id,
                                'move_id': journal.id,
                                'name': 'LC Shipment For LC ' + rec.lc_number,
                                'currency_id': rec.lc_manage_shipment_currency.id,
                                "amount_currency": rec.lc_shipment_acceptance_charge,
                                "debit": rec.lc_shipment_acceptance_charge * rec.lc_manage_shipment_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_shipment_deferred_account.id,
                                'move_id': journal.id,
                                'name': 'LC Shipment For LC ' + rec.lc_number,
                                'currency_id': rec.lc_manage_shipment_currency.id,
                                "amount_currency": rec.lc_shipment_deferred_interest,
                                "debit": rec.lc_shipment_deferred_interest * rec.lc_manage_shipment_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_shipment_charge_account.id,
                                'move_id': journal.id,
                                'name': 'LC Shipment For LC ' + rec.lc_number,
                                'currency_id': rec.lc_manage_shipment_currency.id,
                                "amount_currency": rec.lc_shipment_confirmation,
                                "debit": rec.lc_shipment_confirmation * rec.lc_manage_shipment_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_shipment_pay_account.id,
                                'name': 'LC Shipment For LC ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_manage_shipment_currency.id,
                                "amount_currency": amount * -1,
                                "debit": 0.0,
                                "credit": amount * rec.lc_manage_shipment_currency_rate,
                            }],
                        ],
                    }

                    journal.write(vals)
                    journal.action_post()
                    rec.lc_shipment_journal = journal.id

                    for item in journal.line_ids.filtered(lambda line: line.debit > 0):
                        rec.env['landed.cost.item'].sudo().create({
                            'lc_id': rec.id,
                            'account_id': item.account_id.id,
                            'currency_id': journal.currency_id.id,
                            'label': item.name,
                            'landed_cost_amount': item.debit,
                        })