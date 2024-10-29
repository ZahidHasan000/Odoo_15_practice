from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route

_STATES = [
    ("draft", "User"),
    ("check", "Check"),
    ("approve", "Approved"),
    ("mgt", "MGT"),
    ("cross_function", "Cross Function"),
    ("confirm", "Confirm"),
    ("cancel", "Canceled"),
]


class DoApprovalForm(models.Model):
    _name = 'do.approval.form'
    _description = 'Do Approval Form'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Code')
    date = fields.Date('Date')
    picking_id = fields.Many2one('stock.picking', string="Picking ID")
    picking_type = fields.Many2one('stock.picking.type', string="Picking Type")
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )

    detailed_operation_ids = fields.One2many('detail.operation.product', 'do_approval_id', string='Detailed Operation')
    operation_ids = fields.One2many('operation.product', 'do_approval_id', string='Operation')

    @api.depends('picking_id')
    def get_so_information(self):
        for rec in self:
            if rec.picking_id:
                order = rec.env['sale.order'].sudo().search([('name', '=', rec.picking_id.group_id.name)], limit=1).id
                sale_order = rec.env['sale.order'].browse(order)
                rec['sale_id'] = order if order else False
                rec['customer_name'] = sale_order.partner_id.id if sale_order.partner_id else False
                rec['project_number'] = sale_order.analytic_account_id.id if sale_order.analytic_account_id else False
            else:
                rec['sale_id'] = False
                rec['customer_name'] = False
                rec['project_number'] = False

    sale_id = fields.Many2one('sale.order', compute="get_so_information", string="Sale Order")
    customer_name = fields.Many2one('res.partner', compute="get_so_information", string="Customer")
    project_number = fields.Many2one('account.analytic.account', compute="get_so_information", string='Project Number')

    def send_to_checker(self):
        for rec in self:
            rec.write({'state': 'check'})

    def checker_send_to_approve(self):
        for rec in self:
            rec.write({'state': 'approve'})

    def checker_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def approval_send_to_cross_function(self):
        for rec in self:
            rec.write({'state': 'cross_function'})

    def approval_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def cross_function_approved(self):
        for rec in self:
            rec.picking_id.approve_status = 'approve'
            rec.write({'state': 'confirm'})

    def cross_function_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})


class DetailedOperations(models.Model):
    _name = 'detail.operation.product'

    do_approval_id = fields.Many2one('do.approval.form', string="DO Form ID")
    move_line_id = fields.Many2one('stock.move.line', string="Move Line ID")
    mv_line_id = fields.Integer(string="Line ID")
    product_id = fields.Many2one('product.product', string='Product')
    location_id = fields.Many2one('stock.location', string='Kit From')
    lot_id = fields.Many2one('stock.production.lot', string="Lot/Serial Number")
    product_uom_qty = fields.Float('Reserved')
    qty_done = fields.Float('Done')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')


class OperationProduct(models.Model):
    _name = 'operation.product'

    do_approval_id = fields.Many2one('do.approval.form', string="DO Form ID")
    move_id = fields.Many2one('stock.move', string="Move Line ID")
    mv_id = fields.Integer(string="Line ID")
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float('Demand')
    qty_done = fields.Float('Done')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
