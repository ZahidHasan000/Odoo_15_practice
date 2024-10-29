from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class InheritPurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    sale_order = fields.Many2one('sale.order', string="Sale Order")
    order_item = fields.Many2one('sale.order', string="Sales Order")
    so_business_prod_type = fields.Selection([
        ('genset', 'Genset'),
        ('bbt', 'BBT'),
        ('sub_station', 'Sub-station'),
        ('project', 'Project'),
    ], string='Business Product Type')
    customer_name = fields.Many2one('res.partner', string="Customer Name")
    customer_address = fields.Char(related='customer_name.contact_address_complete', string="Customer Address")
    sales_person = fields.Many2one('hr.employee', string="Sales Person")
    assign_to = fields.Many2one('hr.employee', string="Assign To", tracking=True)

    project_number = fields.Many2one('account.analytic.account', string="Project Number", required=1,
                                     help="It's a Analytic Account Number")

    def button_done(self):
        res = super().button_done()
        if not self.assign_to:
            raise UserError(_('This PR are not assign any employee please assign an employee first !'))
        else:
            if self.assign_to.user_id:
                if self.env.user == self.assign_to.user_id:
                    return res
                else:
                    raise UserError(_('''This logged-in user are not assign to done this PR!
                                    This PR only done %s''', self.assign_to.name))
            else:
                raise UserError(_('No related User in assign to'))

    def create_tender(self):
        for rec in self:
            line_list = []
            for item in rec.line_ids:
                if not item.display_type:
                    line_values = {
                        'product_id': item.product_id.id,
                        'product_description_variants': item.name,
                        'product_qty': item.product_qty,
                        'qty_ordered': 0.00,
                        'product_uom_id': item.product_uom_id.id,
                        'price_unit': item.average_cost,
                    }
                    line_list.append((0, 0, line_values))
            # print(line_list)
            tender = rec.env['purchase.requisition'].create({
                'user_id': rec.requested_by.id,
                'customer_name': rec.customer_name.id,
                'purchase_request': rec.id,
                'line_ids': line_list
            })

            action = {
                'name': _("Purchase Agreements"),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.requisition',
                'target': 'current',
            }

            order = tender.id
            action['res_id'] = order
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('purchase_requisition.view_purchase_requisition_form').id, 'form')]

            return action

    @api.depends('state')
    def _tender_count(self):
        for rec in self:
            if rec.state:
                rec.tender_count = len(
                    self.env['purchase.requisition'].sudo().search([('purchase_request', '=', rec.id)]))

            else:
                rec.tender_count = 0

    tender_count = fields.Integer(compute="_tender_count")

    def view_tender(self):
        self.ensure_one()

        action = {
            'name': _("Purchase Agreements"),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition',
            'target': 'current',
        }
        # invoice_ids = self.invoice_ids.ids
        purchase_request = self.env['purchase.requisition'].sudo().search([('purchase_request', '=', self.id)])

        if len(purchase_request) == 1:
            pr_id = purchase_request.id
            action['res_id'] = pr_id
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('purchase_requisition.view_purchase_requisition_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', purchase_request.ids)]

        return action

    # canopy and ats fields
    is_canopy = fields.Boolean(string='Canopy', default=False)
    canopy_kva_rating = fields.Integer(string="KVA Rating")
    canopy_sound_level = fields.Char(string="Sound Level")
    canopy_sound_level_distance = fields.Char(string="Sound Level Distance")
    type_of_canopy = fields.Selection([
        ('floor_mounting', 'Floor Mounting'),
        ('body_type', 'Body Type')
    ], string='Type of Canopy')
    canopy_hot_air_passing = fields.Selection([
        ('in_front_canopy', 'In front of Canopy'),
        ('top_canopy', 'Top of Canopy')
    ], string='Hot Air Passing')
    canopy_silencer_type = fields.Text(string="Type of Silencer")
    canopy_note = fields.Text(string="Note")

    # ATS
    is_ats = fields.Boolean(string='ATS', default=False)
    ats_kva_rating = fields.Integer(string="KVA Rating")
    ats_amp = fields.Text(string="AMP")
    ats_brand = fields.Selection([
        ('abb', 'ABB'),
        ('schneider', 'Schneider'),
        ('siemens', 'Siemens'),
        ('hyundai', 'Hyundai')
    ], string='Brand')
    ats_note = fields.Text(string="Note")

#   Approver Fields
    approver_comment = fields.Text(string="Note")
    pr_priority = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Low'),
        ('high', 'High'),
        ('very high', 'Very High'),
    ], string='Priority')
    approver_signature = fields.Binary(string='Approver Signature')
    approver_signature_date = fields.Date(string="Date")

    pr_type = fields.Selection([
        ('internal', 'internal'),
        ('external', 'external'),
        ('projects', 'projects'),
        ('general stock', 'General Stock'),
    ], string='PR Type')
    submitted_by_department = fields.Many2one('hr.department', string="Submitted By (Department)")
    user_department = fields.Many2one('hr.department', string="User Department")
    required_by_date = fields.Date(string="Required Date")
    requisition_type = fields.Selection([
        ('regular', 'Regular'),
        ('emergency', 'Emergency'),
    ], string='Requisition Type')
    delivery_location = fields.Selection([
        ('customer site', 'Customer Site'),
        ('warehouse', 'Warehouse'),
        ('head office', 'Head Office'),
        ('sel_factory', 'SEL Factory'),
    ], string='Delivery Location')
    delivery_location_add = fields.Char(string="Customer Delivery Address")
    contact_person = fields.Many2one('hr.employee', string='Contact Person')
    customer_phone = fields.Char('Customer Phone', related='customer_name.phone')
    budget_as_per_design = fields.Float('Budget as per Design')
    payment_type = fields.Selection([
        ('advance100%', 'Advance 100%'),
        ('onsite_delivery100%', 'Onsite Delivery 100%'),
        ('after_delivery100%', 'After Delivery 100%'),
        ('after_delivery100%_15_days', 'After Delivery 100 % within 15 days'),
    ], string='Payment Type')
    pr_justification = fields.Char('Justification')
    pr_note = fields.Text('Note (If any)')

    @api.onchange('delivery_location')
    def get_head_office_address(self):
        for record in self:
            if record.delivery_location == 'head office':
                record.delivery_location_add = ''
                if record.company_id.street:
                    record.delivery_location_add += record.company_id.street + ', '
                if record.company_id.street2:
                    record.delivery_location_add += record.company_id.street2 + ', '
                if record.company_id.zip:
                    record.delivery_location_add += record.company_id.zip + ' '
                if record.company_id.city:
                    record.delivery_location_add += record.company_id.city + ', '
                if record.company_id.state_id:
                    record.delivery_location_add += record.company_id.state_id.name + ', '
                if record.company_id.country_id:
                    record.delivery_location_add += record.company_id.country_id.name

                record.delivery_location_add = record.delivery_location_add.strip().strip(',')
            else:
                record.delivery_location_add = ''

    @api.onchange('project_number')
    def add_line_analytic_account(self):
        for rec in self:
            if rec.line_ids:
                for item in rec.line_ids:
                    item.analytic_account_id = rec.project_number.id
            else:
                pass

    def reserved_stock_quantity(self):
        for rec in self:
            reserve_pr = len(rec.env['stock.picking'].sudo().search([('reserved_pr_ids', '=', rec.id)]))

            line_list = []
            for item in rec.line_ids.filtered(lambda l: l.product_qty > 0 and l.qty_available > 0 and l.product_qty > l.reserved_qty):
                quantity1 = item.product_qty - item.reserved_qty
                quantity2 = quantity1 if quantity1 <= item.qty_available else item.qty_available
                line_values = {
                    'name': item.name,
                    'product_id': item.product_id.id,
                    'product_uom_qty': quantity2,
                    'product_uom': item.product_uom_id.id,
                    'pr_request_line_id': item.id,
                }
                line_list.append((0, 0, line_values))
            # print(line_list)
            transfer_ctx = dict(
                default_reserved_pr_ids=rec.id,
                default_purchase_req_id=rec.id,
                default_origin=rec.name,
                default_move_ids_without_package=line_list,
            )
            # print(transfer_ctx)
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            return {
                'name': 'Transfers',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                "domain": [('reserved_pr_ids', '=', rec.id)],
                "views": form_view,
                'context': transfer_ctx,
            }

    reserved_transfers = fields.Many2many('stock.picking', string="Reserved Transfers")

    @api.depends('reserved_transfers')
    def _reserved_transfer_count(self):
        for rec in self:
            if rec.reserved_transfers:
                rec.reserved_transfer_count = len(rec.reserved_transfers)
            else:
                rec.reserved_transfer_count = 0
    reserved_transfer_count = fields.Integer(compute='_reserved_transfer_count')

    def view_reserved_transfer(self):
        self.ensure_one()

        action = {
            'name': _("Transfers"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'target': 'current',
        }
        # invoice_ids = self.invoice_ids.ids

        if len(self.reserved_transfers) == 1:
            picking_id = self.reserved_transfers.id
            action['res_id'] = picking_id
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', self.reserved_transfers.ids)]

        return action

    def create_procurement(self):
        for rec in self:
            line_list = []
            for item in rec.line_ids.filtered(lambda l: l.product_qty - (l.reserved_qty + l.procurement_qty) > l.qty_available):
                # if item.product_qty > item.procurement_qty:
                line_values = {
                    'product_id': item.product_id.id,
                    'product_description_variants': item.name,
                    'product_qty': (item.product_qty - (item.reserved_qty + item.procurement_qty)) - item.qty_available,
                    'pr_request_line_id': item.id,
                    'qty_ordered': 0.00,
                    'product_uom_id': item.product_uom_id.id,
                    'price_unit': item.average_cost,
                }
                line_list.append((0, 0, line_values))

            tender_ctx = dict(
                default_user_id=rec.requested_by.id,
                default_customer_name=rec.customer_name.id,
                default_purchase_request=rec.id,
                default_line_ids=line_list,
            )
            # print(transfer_ctx)
            form_view = [(self.env.ref('purchase_requisition.view_purchase_requisition_form').id, 'form')]
            return {
                'name': 'Purchase Agreements',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.requisition',
                "domain": [('purchase_request', '=', rec.id)],
                "views": form_view,
                'context': tender_ctx,
            }

    procurement_ids = fields.Many2many('purchase.requisition', string="Agreements IDS")

    @api.depends('procurement_ids')
    def _procurement_count(self):
        for rec in self:
            if rec.procurement_ids:
                rec.procurement_count = len(rec.procurement_ids)
            else:
                rec.procurement_count = 0

    procurement_count = fields.Integer(compute='_procurement_count')
    reserved_done = fields.Boolean(string="Reserved Done", default=False)

    def view_procurement(self):
        self.ensure_one()

        action = {
            'name': _("Transfers"),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition',
            'target': 'current',
        }
        # invoice_ids = self.invoice_ids.ids

        if len(self.procurement_ids) == 1:
            procurement_id = self.procurement_ids.id
            action['res_id'] = procurement_id
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('purchase_requisition.view_purchase_requisition_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', self.procurement_ids.ids)]

        return action


class InheritPurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    is_sale_pr = fields.Boolean('Is Sale PR', default=False)
    ref_bom_id = fields.Many2one('mrp.bom', string="BOM ID")
    sale_order_id = fields.Many2one('sale.order', related="request_id.order_item", string="Sale Order")
    # order_line_item = fields.Many2many('sale.order', related="request_id.order_item", string="Sale Order")
    sale_order_line = fields.Many2one('sale.order.line', domain="[('order_id', '=', sale_order_id)]",
                                      string="Sale Order Line")
    reserved_qty = fields.Float(string="Reserved Qty")
    procurement_qty = fields.Float(string="Procurement Qty")

    @api.onchange('product_id')
    def get_analytic_account(self):
        for rec in self:
            if rec.product_id:
                rec.analytic_account_id = rec.request_id.project_number.id
            else:
                rec.analytic_account_id = False

    @api.depends('product_id')
    def get_total_current_stock(self):
        for rec in self:
            if rec.product_id:
                location_ids = []
                location = rec.env['stock.location'].sudo().search([('quantity_count_pr', '=', True)])
                for loc in location:
                    location_ids.append(loc.id)

                # print(location_ids)
                total_quantity = []
                stock_quant = rec.env['stock.quant'].sudo().search([('location_id', 'in', location_ids),
                                                                    ('product_id', '=', rec.product_id.id)])
                for quant in stock_quant:
                    total_quantity.append(quant.quantity)
                print(total_quantity)
                rec['qty_available'] = sum(total_quantity)
            else:
                rec['qty_available'] = 0.00

    qty_available = fields.Float(compute="get_total_current_stock", string="Current Stock")


class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    quantity_count_pr = fields.Boolean(string="PR Count Quantity", default=False)


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockPickingInherit, self).create(vals_list)
        if res.reserved_pr_ids:
            res.reserved_pr_ids.reserved_transfers = [(4, res.id)]
        return res

    def button_validate(self):
        if self.picking_type_code == 'internal':
            if self.validate_by_user and self.env.user.id == self.validate_by_user.id:
                res = super(StockPickingInherit, self).button_validate()

                for item in self.move_ids_without_package:
                    if item.pr_request_line_id:
                        item.pr_request_line_id.reserved_qty += item.quantity_done
                    else:
                        pass
                self.reserved_pr_ids.reserved_done = True
                return res
            elif self.validate_by_user and self.env.user.id != self.validate_by_user.id:
                raise UserError(_('''You are not allowed to validate this transfer'''))
            else:
                raise UserError(_('''Please Select Validate by First !'''))

        else:
            res = super(StockPickingInherit, self).button_validate()

            for item in self.move_ids_without_package:
                if item.pr_request_line_id:
                    item.pr_request_line_id.reserved_qty += item.quantity_done
                else:
                    pass
            self.reserved_pr_ids.reserved_done = True
            return res

    reserved_pr_ids = fields.Many2one('purchase.request', string="Reserved PR")
    validate_by_user = fields.Many2one('res.users', string="Validate by")


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    pr_request_line_id = fields.Many2one('purchase.request.line', string="Request ID")


class TenderLineInherit(models.Model):
    _inherit = 'purchase.requisition.line'

    pr_request_line_id = fields.Many2one('purchase.request.line', string="Request Line ID")


class TenderInherit(models.Model):
    _inherit = 'purchase.requisition'

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',
                                      required=True, default=False, domain="['|',('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(TenderInherit, self).create(vals_list)
        if res.purchase_request:
            res.purchase_request.procurement_ids = [(4, res.id)]
            for item in res.line_ids:
                if item.pr_request_line_id:
                    item.pr_request_line_id.procurement_qty += item.product_qty
        return res

    def unlink(self):
        # Draft requisitions could have some requisition lines.
        if self.purchase_request:
            self.purchase_request.procurement_ids = False
            for item in self.line_ids:
                if item.pr_request_line_id:
                    item.pr_request_line_id.procurement_qty = 0.00
        return super(TenderInherit, self).unlink()

    def action_cancel(self):
        if self.purchase_request:
            self.purchase_request.procurement_ids = False
            for item in self.line_ids:
                if item.pr_request_line_id:
                    item.pr_request_line_id.procurement_qty = 0.00

        return super(TenderInherit, self).action_cancel()


class PurchaseOrderInitiatedBy(models.Model):
    _inherit = 'purchase.order'

    def user_send_quotation_to_check(self):
        self.initiated_by = self.env.user.id
        return super().user_send_quotation_to_check()

    initiated_by = fields.Many2one('res.users', string="Initiated By")

    # @api.onchange('requisition_id')
    # def _onchange_requisition_id(self):
    #     super(PurchaseOrderInitiatedBy, self)._onchange_requisition_id()
    #     if self.requisition_id:
    #         self.picking_type_id = False

    @api.onchange('company_id')
    def _onchange_company_id(self):
        p_type = self.picking_type_id
        # print('joyanto joyanto')
        if not (p_type and p_type.code == 'incoming' and (
                p_type.warehouse_id.company_id == self.company_id or not p_type.warehouse_id)):
            self.picking_type_id = False
