from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class InvoiceAdvanceStatus(models.Model):
    _inherit = 'account.move'

    invoice_origin = fields.Char(string='Origin', readonly=True, tracking=True, help="The document(s) that generated the invoice.")
    advance_inv_status = fields.Selection([
        ('regular_inv', 'Regular Invoice'),
        ('advance_inv', 'Advance Invoice')
    ], string='Invoice State')
    inv_customer_po_number=fields.Char(compute='get_so_customer_po_inv',string="Customer PO Number",store=True)
    
    @api.depends('invoice_origin')
    def get_so_customer_po_inv(self):
        for rec in self:
            so=self.env['sale.order'].sudo().search([('name','=',rec.invoice_origin)])
            if so:
                rec.inv_customer_po_number=so.so_customer_po_number
            else:
                rec.inv_customer_po_number=False


