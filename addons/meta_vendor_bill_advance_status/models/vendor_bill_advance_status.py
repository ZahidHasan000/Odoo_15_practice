##############################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time


class VendorBillAdvanceStatus(models.Model):
    _inherit = 'account.move'

    advance_bill_status = fields.Selection([
        ('regular_bill', 'Regular Bill'),
        ('advance_bill', 'Advance Bill')
    ], string='Bill Status', default=False)


class PurchaseOrderAdvanceRegular(models.Model):
    _inherit = 'purchase.order'

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        # print('Hit to Regular Bill')
        invoice_vals.update({'advance_bill_status': 'regular_bill'})
        return invoice_vals


