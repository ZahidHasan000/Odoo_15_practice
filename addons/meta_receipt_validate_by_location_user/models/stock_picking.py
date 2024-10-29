from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class StockPickingReceiptValidate(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if self.picking_type_code == 'incoming':
            if self.location_dest_id.validate_users and self.env.user.id in self.location_dest_id.validate_users.ids:
                return super(StockPickingReceiptValidate, self).button_validate()

            elif self.location_dest_id.validate_users and self.env.user.id not in self.location_dest_id.validate_users.ids:
                raise UserError(_('''You are not allowed to validate this transfer,\n please contact your settings administrator'''))

            elif not self.location_dest_id.validate_users:
                raise UserError(_('''This operation type destination location here validation users are not set,\n please contact your settings administrator'''))

        else:
            return super(StockPickingReceiptValidate, self).button_validate()


