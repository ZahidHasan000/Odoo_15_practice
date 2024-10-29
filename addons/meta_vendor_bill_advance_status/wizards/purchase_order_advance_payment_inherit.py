##############################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time


class PurchaseOrderAdvancePaymentInherit(models.TransientModel):
    _inherit = 'purchase.order.advance.payment'

    def _prepare_invoice_values(self, order, name, amount, so_line):
        vals = super()._prepare_invoice_values(order, name, amount, so_line)
        vals.update({
            'advance_bill_status': 'advance_bill'
        })
        return vals
