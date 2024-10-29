from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    country_of_origin = fields.Many2one('res.country', string="COO")

    quality = fields.Char('Quality')
    responsive = fields.Char('Responsive')

    po_sourcing_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], default='local',
                                     string="Sourcing Type")
    custom_duty = fields.Float('Custom Duty')
    freight_charge = fields.Float('Freight Charge')
    bank_and_insurance = fields.Float('Bank & Insurance')
    c_and_f_commission = fields.Float('C&F Commission')
    customer_name = fields.Many2one('res.partner', string="Customer Name")
    customer_address = fields.Char(related='customer_name.contact_address_complete', string="Customer Address")
    customer_reference = fields.Many2one('account.analytic.account', string="Customer Reference")

    @api.onchange('requisition_id')
    def get_tender_program_number(self):
        for rec in self:
            if rec.requisition_id:
                rec['customer_name'] = rec.requisition_id.customer_name.id if rec.requisition_id.customer_name else False
                rec['customer_reference'] = rec.requisition_id.project_number.id if rec.requisition_id.project_number else False

            else:
                rec['customer_name'] = False
                rec['customer_reference'] = False


