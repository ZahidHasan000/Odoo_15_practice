from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    approval_id = fields.Many2one('do.approval.form', string="Approval")
    delivery_location = fields.Text(string="Delivery Location")
    contact = fields.Selection([
        ("contact_add", "Contact Address"),
        ("delivery_add", "Delivery Address"),
    ], string="Contact", tracking=True)
    contact_name = fields.Char('Name')
    contact_address = fields.Char('Address')

    @api.onchange('contact')
    def get_contact_domain(self):
        for rec in self:
            if rec.partner_id.child_ids:
                if rec.contact == 'contact_add':
                    rec.select_con_del_partner = False
                    rec.contact_address = ''
                    contact_address = rec.env['res.partner'].sudo().search([('parent_id', '=', rec.partner_id.id),
                                                                            ('type', '=', 'contact')])
                    if len(contact_address) > 1:
                        res = {'domain': {'select_con_del_partner': ['&', ('parent_id', '=', rec.partner_id.id),
                                                                     ('type', '=', 'contact')]}}
                    elif len(contact_address) == 1:
                        rec.select_con_del_partner = contact_address.id
                        res = {'domain': {'select_con_del_partner': ['&', ('parent_id', '=', rec.partner_id.id),
                                                                     ('type', '=', 'contact')]}}
                    else:
                        rec.contact_address = rec.partner_id.contact_address_complete
                        res = {'domain': {'select_con_del_partner': ['&', ('parent_id', '=', rec.partner_id.id),
                                                                     ('type', '=', 'contact')]}}

                elif rec.contact == 'delivery_add':
                    rec.select_con_del_partner = False
                    rec.contact_address = ''
                    delivery_address = rec.env['res.partner'].sudo().search([('parent_id', '=', rec.partner_id.id),
                                                                            ('type', '=', 'delivery')])
                    if len(delivery_address) > 1:
                        res = {'domain': {'select_con_del_partner': ['&', ('parent_id', '=', rec.partner_id.id),
                                                                     ('type', '=', 'delivery')]}}
                    elif len(delivery_address) == 1:
                        rec.select_con_del_partner = delivery_address.id
                        res = {'domain': {'select_con_del_partner': ['&', ('parent_id', '=', rec.partner_id.id),
                                                                     ('type', '=', 'delivery')]}}
                    else:
                        rec.contact_address = rec.partner_id.contact_address_complete
                        res = {'domain': {'select_con_del_partner': ['&', ('parent_id', '=', rec.partner_id.id),
                                                                     ('type', '=', 'contact')]}}

                else:
                    rec.select_con_del_partner = False
                    rec.contact_address = ''
                    res = {'domain': {'select_con_del_partner': [('parent_id', '=', rec.partner_id.id)]}}
            else:
                rec.select_con_del_partner = False
                rec.contact_address = ''
                res = {'domain': {'select_con_del_partner': [('parent_id', '=', rec.partner_id.id)]}}

        return res

    select_con_del_partner = fields.Many2one('res.partner', string="Select Contact")

    @api.onchange('select_con_del_partner')
    def get_contact_address_details(self):
        for rec in self:
            if rec.select_con_del_partner.type == 'contact':
                rec.contact_name = rec.select_con_del_partner.name
                rec.contact_address = ''
                if rec.select_con_del_partner.title:
                    rec.contact_address += 'Title: ' + rec.select_con_del_partner.title.name + ', '
                if rec.select_con_del_partner.function:
                    rec.contact_address += 'Position: ' + rec.select_con_del_partner.function + ', '
                if rec.select_con_del_partner.email:
                    rec.contact_address += 'Email: ' + rec.select_con_del_partner.email + ', '
                if rec.select_con_del_partner.phone:
                    rec.contact_address += 'Phone: ' + rec.select_con_del_partner.phone
                rec.contact_address = rec.contact_address.strip().strip(',')

            elif rec.select_con_del_partner.type == 'delivery':
                rec.contact_name = rec.select_con_del_partner.name
                rec.contact_address = ''
                if rec.select_con_del_partner.street:
                    rec.contact_address += rec.select_con_del_partner.street + ', '
                if rec.select_con_del_partner.zip:
                    rec.contact_address += rec.select_con_del_partner.zip + ', '
                if rec.select_con_del_partner.city:
                    rec.contact_address += rec.select_con_del_partner.city + ', '
                if rec.select_con_del_partner.state_id:
                    rec.contact_address += rec.select_con_del_partner.state_id.name + ', '
                if rec.select_con_del_partner.country_id:
                    rec.contact_address += rec.select_con_del_partner.country_id.name + ', '
                if rec.select_con_del_partner.phone:
                    rec.contact_address += 'Phone: ' + rec.select_con_del_partner.phone + ', '
                if rec.select_con_del_partner.email:
                    rec.contact_address += 'Email: ' + rec.select_con_del_partner.email
                rec.contact_address = rec.contact_address.strip().strip(',')
            else:
                pass

    def create_approval(self):
        for rec in self:
            line_list1 = []
            line_list2 = []
            for item1 in rec.move_line_ids_without_package:
                line_values1 = {
                    'move_line_id': item1.id,
                    'mv_line_id': int(item1.id),
                    'product_id': item1.product_id.id,
                    'location_id': item1.location_id.id,
                    'lot_id': item1.lot_id.id,
                    'product_uom_qty': item1.product_uom_qty,
                    'qty_done': item1.qty_done,
                    'product_uom_id': item1.product_uom_id.id,
                }
                line_list1.append((0, 0, line_values1))

            for item2 in rec.move_ids_without_package:
                line_values2 = {
                    'move_id': item2.id,
                    'mv_id': int(item2.id),
                    'product_id': item2.product_id.id,
                    'product_uom_qty': item2.product_uom_qty,
                    'qty_done': item2.quantity_done,
                    'product_uom_id': item2.product_uom.id,
                }
                line_list2.append((0, 0, line_values2))

            delivery_approval = rec.env['do.approval.form'].create({
                'name': rec.name,
                'date': fields.Date.today(),
                'picking_id': rec.id,
                'picking_type': rec.picking_type_id.id,
                'detailed_operation_ids': line_list1,
                'operation_ids': line_list2
            })

            rec.approval_id = delivery_approval.id

            action = {
                'name': _("Transfer"),
                'type': 'ir.actions.act_window',
                'res_model': 'do.approval.form',
                'target': 'current',
            }

            do_id = delivery_approval.id
            action['res_id'] = do_id
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('meta_do_extra_form_approval.view_do_approval_form').id, 'form')]

            return action

    @api.depends('state')
    def _do_approval_count(self):
        for rec in self:
            if rec.approval_id:
                rec.approval_count = len(
                    self.env['do.approval.form'].sudo().search([('id', '=', rec.approval_id.id),
                                                            ('state', '!=', 'cancel')]))

            else:
                rec.approval_count = 0

    approval_count = fields.Integer(compute="_do_approval_count")

    approve_status = fields.Selection([
        ('pending', 'RFA'),
        ('approve', 'Approved'),
        ], string='Approval Status', default='pending')

    def view_transfer_approval(self):
        self.ensure_one()

        action = {
            'name': _("Transfer"),
            'type': 'ir.actions.act_window',
            'res_model': 'do.approval.form',
            'target': 'current',
        }
        # invoice_ids = self.invoice_ids.ids
        approval_do_id = self.env['do.approval.form'].sudo().search([('id', '=', self.approval_id.id),
                                                                     ('state', '!=', 'cancel')])

        if len(approval_do_id) == 1:
            order_id = approval_do_id.id
            action['res_id'] = order_id
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('meta_do_extra_form_approval.view_do_approval_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', approval_do_id.ids)]

        return action

    def action_cancel(self):
        res = super().action_cancel()
        self.cancel_approval_transfer()
        return res

    def cancel_approval_transfer(self):
        for rec in self:
            if rec.approval_id:
                rec.env['do.approval.form'].sudo().search([('id', '=', rec.approval_id.id)]).unlink()

            else:
                pass

    @api.depends('group_id')
    def get_customer_ref(self):
        for rec in self:
            if rec.group_id:
                if rec.group_id:
                    purchase_order = rec.env['purchase.order'].sudo().search([('name', '=', rec.group_id.name)])
                    sales_order = rec.env['sale.order'].sudo().search([('name', '=', rec.group_id.name)])
                    if purchase_order and rec.picking_type_code == 'incoming':
                        rec['customer_name'] = purchase_order.customer_name.id
                        rec['customer_reference'] = purchase_order.customer_reference.id
                    elif sales_order and rec.picking_type_code == 'outgoing':
                        rec['customer_name'] = False
                        rec['customer_reference'] = sales_order.analytic_account_id.id
                    else:
                        rec['customer_name'] = False
                        rec['customer_reference'] = False
                else:
                    rec['customer_name'] = False
                    rec['customer_reference'] = False
            else:
                rec['customer_name'] = False
                rec['customer_reference'] = False

    customer_name = fields.Many2one('res.partner', compute="get_customer_ref", string="Customer Name")
    customer_reference = fields.Many2one('account.analytic.account', compute="get_customer_ref", string="Customer Reference")

