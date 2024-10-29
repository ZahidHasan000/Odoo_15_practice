from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    def open_transfer_view(self):
        self.ensure_one()

        action = {
            'name': _("Transfers"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'target': 'current',
        }
        # invoice_ids = self.invoice_ids.ids
        transfer_number = self.env['stock.picking'].sudo().search([('name', '=', self.reference)])

        if len(transfer_number) == 1:
            tf_id = transfer_number.id
            action['res_id'] = tf_id
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', transfer_number.ids)]

        return action

    def open_order_form_purchase(self):
        print('#$#$#$#$#$#$')

    def open_order_form_sales(self):
        print('#$#$#$#$#$#$')

