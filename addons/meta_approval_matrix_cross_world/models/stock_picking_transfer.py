
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[
        ('draft', 'User'),
        ('check', 'Check'),
        ('approved', 'Approved'),
        ('cross_function', 'Cross Function'),
        ('waiting',),
        ('confirmed',),
        ('assigned',),
        ('done',),
        ('cancel',),
    ], default='draft',
        ondelete={'draft': 'cascade', 'check': 'cascade', 'approved': 'cascade', 'cross_function': 'cascade',
                  'waiting': 'cascade', 'confirmed': 'cascade', 'assigned': 'cascade', 'done': 'cascade', 'cancel': 'cascade'})

    approval_picking_type = fields.Selection([
        ('in', 'IN'),
        ('out', 'OUT'),
        ('none', 'NONE'),
    ], string='Picking Type',)

    def user_picking_send_to_check(self):
        for rec in self:
            if rec.picking_type_id.sequence_code == 'IN':
                rec.approval_picking_type = 'in'
            elif rec.picking_type_id.sequence_code == 'OUT':
                rec.approval_picking_type = 'out'
            else:
                rec.approval_picking_type = 'none'
            rec.write({'state': 'check'})

    def checker_picking_send_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})

    def checker_cancel_picking(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def approved_send_picking_to_cross_function(self):
        for rec in self:
            rec.write({'state': 'cross_function'})

    def approved_cancel_picking(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    # def cross_function_picking_(self):
    #     for rec in self:
    #         rec.write({'state': 'draft'})

    def cross_function_cancel_picking(self):
        for rec in self:
            rec.write({'state': 'cancel'})

