# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrderWizard(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    pr_request_id = fields.Many2one('purchase.request', string="Request ID", tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency ID", tracking=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)
        request_line_ids = []
        if active_model == "purchase.request.line":
            request_line_ids += self.env.context.get("active_ids", [])
            request_line_ids2 = self.env.context.get("active_ids", False)
            request = self.env[active_model].browse(request_line_ids2)
            res['pr_request_id'] = request.request_id[0]
            res['currency_id'] = request.request_id[0].currency_id.id
            print(request.request_id[0])
        elif active_model == "purchase.request":
            request_ids = self.env.context.get("active_ids", False)
            request = self.env[active_model].browse(request_ids)
            res['pr_request_id'] = request.id
            res['currency_id'] = request.currency_id.id
            request_line_ids += (
                self.env[active_model].browse(request_ids).mapped("line_ids.id")
            )
        if not request_line_ids:
            return res

        res["item_ids"] = self.get_items(request_line_ids)
        # res["pr_request_id"] = self.item_ids.request_id[0]
        request_lines = self.env["purchase.request.line"].browse(request_line_ids)
        supplier_ids = request_lines.mapped("supplier_id").ids
        if len(supplier_ids) == 1:
            res["supplier_id"] = supplier_ids[0]
        return res

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        if not self.supplier_id:
            raise UserError(_("Enter a supplier."))
        supplier = self.supplier_id
        data = {
            "origin": origin,
            "partner_id": self.supplier_id.id,
            "currency_id": self.currency_id.id if self.currency_id else False,
            "purchase_request": self.pr_request_id.id if self.pr_request_id else False,
            "fiscal_position_id": supplier.property_account_position_id
            and supplier.property_account_position_id.id
            or False,
            "picking_type_id": picking_type.id,
            "company_id": company.id,
            "group_id": group_id.id,
        }
        return data
