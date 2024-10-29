##############################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

class SaleeOrderAdvancePaymentInherit(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    # def _prepare_invoice_values(self, order, name, amount, so_line):
    #     vals = super()._prepare_invoice_values(order, name, amount, so_line)
    #     if self.advance_payment_method in ['percentage','fixed']:
    #         logging.info(f"advance_payment_method---------------->{self.advance_payment_method}")
    #         vals.update({
    #             'advance_inv_status': 'advance_inv'
    #         })            
    #     else:
    #         logging.info(f"advance_payment_method---------------->{self.advance_payment_method}")
    #         vals.update({
    #             'advance_inv_status': 'regular_inv'
    #         })
    #     # else:
    #     #     vals.update({
    #     #         'advance_inv_status': False
    #     #     })

    #     return vals
    
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':            
            invoice_id=sale_orders._create_invoices(final=self.deduct_down_payments)
            invoice_id.advance_inv_status= 'regular_inv'
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                amount, name = self._get_advance_details(order)

                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

                so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
                so_line = sale_line_obj.create(so_line_values)
                invoice_id=self._create_invoice(order, so_line, amount)
                invoice_id.advance_inv_status= 'advance_inv'
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
