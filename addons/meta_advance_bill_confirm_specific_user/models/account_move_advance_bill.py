##############################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time


class AccountMoveAdvanceBillInherit(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for rec in self:
            if rec.move_type == 'in_invoice':
                if rec.advance_bill_status == 'advance_bill' \
                    and not rec.env.user.has_group('meta_advance_bill_confirm_specific_user.access_confirm_advance_bill'):
                    raise UserError(_('You are not Allowed to Confirm this advance Bill. Bill No: %s') % rec.name)
                else:
                    return super().action_post()

            else:
                return super().action_post()


class AccountPaymentSignedUser(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        for rec in self:
            if rec.payment_type == 'outbound':
                if not rec.env.user.has_group('meta_approval_matrix_cross_world.signed_approval'):
                    raise UserError(_('You are not allowed to confirm this payment, this payment confirm only signed approval users'))
                else:
                    return super().action_post()
            else:
                return super().action_post()

