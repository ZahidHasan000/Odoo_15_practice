
from odoo import api, fields, models, _


class PurchaseComparison(models.Model):
    _inherit = 'comparison'

    def test_create_confirm_po(self):
        for line in self.select_product_ids.filtered(lambda l: l.marking_product):
            if line:
                order_line = self.env['purchase.order.line'].sudo().search([('id', '=', line.product_line_id)])

                order = self.env['purchase.order'].sudo().search([('id', '=', order_line.order_id.id)])
                order2 = self.env['purchase.order'].sudo().search([('against_po_id', '=', str(order_line.order_id.id))])
                # if not order2:
                order = self.env['purchase.order'].create({
                    'partner_id': order.partner_id.id,
                    'partner_ref': order.partner_ref,
                    'payment_terms': order.payment_terms,
                    'country_of_origin': order.country_of_origin.id,
                    'origin': order.requisition_id.name,
                    'requisition_id': order.requisition_id.id,
                    'customer_name': order.customer_name.id,
                    'customer_reference': order.customer_reference.id,
                    'purchase_request': order.purchase_request.id,
                    'currency_id': order.currency_id.id,
                    'against_po_id': str(order.id),
                    'comparison_id': self.id,
                    'po_comments': order.po_comments,
                    'warranty': order.warranty,
                    'delivery_schedule': order.delivery_schedule,
                    'incoterm_id': order.incoterm_id.id,
                    'po_sourcing_type': order.po_sourcing_type,
                    'custom_duty': order.custom_duty,
                    'freight_charge': order.freight_charge,
                    'bank_and_insurance': order.bank_and_insurance,
                    'c_and_f_commission': order.c_and_f_commission,
                    'order_line': [(0, 0, {
                        'name': order_line.product_id.name,
                        'product_id': order_line.product_id.id,
                        'product_qty': order_line.product_qty,
                        'product_uom': order_line.product_uom.id,
                        'price_unit': order_line.price_unit,
                    })]
                })

                order.write({'state': 'user'})

                action = {
                    'name': _("Order"),
                    'type': 'ir.actions.act_window',
                    'res_model': 'purchase.order',
                    'target': 'current',
                }
                # invoice_ids = self.invoice_ids.ids
                comparison = self.env['purchase.order'].sudo().search([('id', '=', order.id)])

                # if len(comparison) == 1:
                order = comparison.id
                action['res_id'] = order
                action['view_mode'] = 'form'
                action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]

                return action
