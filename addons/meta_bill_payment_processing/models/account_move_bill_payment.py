from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    @api.depends('move_type')
    def get_payment_status(self):
        for rec in self:
            list_payment = []
            if rec.move_type == 'in_invoice':
                payment = rec.env['account.payment'].sudo().search([('state', 'not in', ('posted', 'cancel'))])
                if any(payment.inv_bill_ids.filtered(lambda p: p.id == rec.id)):
                    rec['bill_payment_status'] = 'payment_process'
                else:
                    rec['bill_payment_status'] = 'none'

            else:
                rec['bill_payment_status'] = 'none'
                # for item in payment.inv_bill_ids.filtered(lambda p: p.move_type == 'in_invoice'):

    bill_payment_status = fields.Selection([
        ('none', ''),
        ('payment_process', 'In Process')
    ], compute="get_payment_status", default='none', string='Bill Payment Status')

    def action_register_payment(self):
        for rec in self:
            if rec.move_type == 'in_invoice' and rec.bill_payment_status == 'payment_process':
                raise UserError(_('All-ready a Payment Process is Running, First Confirm the Running Payment Then Make Another Payment!'))
            else:
                return super().action_register_payment()

