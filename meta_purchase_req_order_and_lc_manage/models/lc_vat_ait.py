
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta

import json
import requests
# from urllib.parse import urlparse
import urllib.parse


class LcManageVatAitInherit(models.Model):
    _inherit = 'lc.management'

    #LC Shipment
    lc_manage_vat_ait_date = fields.Date('Date')
    lc_manage_vat_ait_currency = fields.Many2one('res.currency', string='Currency')
    lc_manage_vat_ait_currency_rate = fields.Float(string='Currency Rate BDT', default=1.00, digits=(16, 12))
    lc_manage_ait_import = fields.Float(string="AIT on Import")
    lc_manage_vat_import = fields.Float(string="VAT on Import")
    lc_manage_ait_account = fields.Many2one('account.account', string="AIT Account")
    lc_manage_vat_account = fields.Many2one('account.account', string="VAT Account")
    lc_manage_vat_ait_pay_account = fields.Many2one('account.account', string="Payment Account")
    lc_manage_vat_ait_journal = fields.Many2one('account.move', string="VAT and AIT Journal")

    @api.onchange('lc_manage_vat_ait_currency')
    def get_lc_manage_vat_ait_currency_rate(self):
        if self.lc_manage_vat_ait_currency:
            company = self.env.company
            today_date = self.lc_manage_vat_ait_date if self.lc_manage_vat_ait_date else fields.Date.today()
            from_currency = self.env.company.currency_id
            to_currency = self.lc_manage_vat_ait_currency

            rates = self.env['res.currency']._get_conversion_rate(from_currency, to_currency, company, today_date)
            final_rate = 100.00 / rates
            self.lc_manage_vat_ait_currency_rate = final_rate / 100.00
        else:
            self.lc_manage_vat_ait_currency_rate = 1.00

    def create_lc_vat_ait_journal(self):
        for rec in self:
            # amount = rec.lc_shipment_acceptance_charge + rec.lc_shipment_deferred_interest + rec.lc_shipment_confirmation
            if not rec.lc_manage_vat_ait_journal:
                reference = 'LC VAT & AIT For LC ' + str(rec.lc_number)
                # journal_id = rec.env['account.journal'].sudo().search([['name', '=', 'LC Management']], limit=1).id
                journal_id = rec.default_journal.id
                journal = rec.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': reference,
                    'date': rec.lc_manage_vat_ait_date if rec.lc_manage_vat_ait_date else fields.Date.today(),
                    'journal_id': journal_id,
                    'currency_id': rec.env.company.currency_id.id
                })

                if journal:
                    total_amount = rec.lc_manage_vat_import + rec.lc_manage_ait_import
                    vals = {
                        "line_ids": [
                            [0, 0, {
                                "account_id": rec.lc_manage_ait_account.id,
                                'move_id': journal.id,
                                'name': 'LC AIT For LC ' + rec.lc_number,
                                'currency_id': rec.lc_manage_vat_ait_currency.id,
                                "amount_currency": rec.lc_manage_ait_import,
                                "debit": rec.lc_manage_ait_import * rec.lc_manage_vat_ait_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_manage_vat_account.id,
                                'move_id': journal.id,
                                'name': 'LC VAT For LC ' + rec.lc_number,
                                'currency_id': rec.lc_manage_vat_ait_currency.id,
                                "amount_currency": rec.lc_manage_vat_import,
                                "debit": rec.lc_manage_vat_import * rec.lc_manage_vat_ait_currency_rate,
                                "credit": 0.0,
                            }],
                            [0, 0, {
                                "account_id": rec.lc_manage_vat_ait_pay_account.id,
                                'name': 'LC VAT & AIT For LC ' + rec.lc_number,
                                'move_id': journal.id,
                                'currency_id': rec.lc_manage_vat_ait_currency.id,
                                "amount_currency": total_amount * -1,
                                "debit": 0.0,
                                "credit": total_amount * rec.lc_manage_vat_ait_currency_rate,
                            }],
                        ],
                    }

                    journal.write(vals)
                    journal.action_post()
                    rec.lc_manage_vat_ait_journal = journal.id
