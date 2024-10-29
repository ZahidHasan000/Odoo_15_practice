
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderDeliverTo(models.Model):
    _inherit = 'purchase.order'

    picking_operation_type = fields.Many2one('stock.picking.type', string="Deliver To", Tracking=True)

    @api.onchange('picking_operation_type')
    def get_picking_operation(self):
        if self.picking_operation_type:
            self.picking_type_id = self.picking_operation_type.id
        else:
            self.picking_type_id = False

    def send_to_user(self):
        if self.picking_operation_type:
            return super().send_to_user()
        else:
            raise UserError(_('You are not select Deliver to Please Select Delivery to First!'))

    def user_send_quotation_to_check(self):
        if self.picking_operation_type:
            return super().user_send_quotation_to_check()
        else:
            raise UserError(_('You are not select Deliver to Please Select Delivery to First!'))
