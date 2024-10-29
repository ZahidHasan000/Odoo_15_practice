from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta

_STATES = [
    ("draft", "Draft"),
    ("done", "Done"),
    ("cancel", "Canceled"),
]


class ServiceProductAre(models.Model):
    _name = 'service.product'
    _description = "Service Products"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Name", required=True, readonly=True,
                       index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string="Receive From")
    date = fields.Date(
        string='Date',
        index=True,
        readonly=True,
        copy=False,
        default=fields.Date.context_today
    )

    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )

    source_document = fields.Many2one('purchase.order', string='Source Document', readonly=1, store=True)
    product_line = fields.One2many('service.product.line', 'service_product_id', string='Product Lines')

    @api.model
    def create(self, vals):
        # if not vals.get('name') or vals['name'] == _('New'):
        vals['name'] = self.env['ir.sequence'].next_by_code('seq.po.service.item') or _('New')
        return super(ServiceProductAre, self).create(vals)

    def action_confirm(self):
        for rec in self.product_line:
            if rec.done_qty > 0.0:
                rec.purchase_order_line_id.qty_received = rec.done_qty
        return self.write({"state": "done"})
    
    def write(self, vals):
        res = super(ServiceProductAre, self).write(vals)
        if vals.get("product_line"):
            for item in self.product_line:
                print('/*/*//*/*/*/*/*')
                item.purchase_order_line_id.qty_received = item.done_qty

        return res

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        # if self.env.context.get('mark_so_as_sent'):
        #     self.filtered(lambda o: o.state == 'draft').with_context(tracking_disable=True).write({'state': 'sent'})
        return super(ServiceProductAre, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)


class ServiceProductLine(models.Model):
    _name = 'service.product.line'
    _order = "id asc"
    _description = "Service Product Line"

    name = fields.Char('Name')
    service_product_id = fields.Many2one('service.product', string="Service Products ID")
    product = fields.Many2one('product.product', string='Product')
    purchase_order_line_id = fields.Many2one('purchase.order.line', string="Purchase Line ID")
    order_qty = fields.Float(string="Order Qty")
    done_qty = fields.Float(string="Done Qty")

    def write(self, values):
        if 'done_qty' in values:
            for line in self:
                line._track_service_qty_received(values['done_qty'])

        return super(ServiceProductLine, self).write(values)

    def _track_service_qty_received(self, new_qty):
        self.ensure_one()
        if new_qty != self.done_qty:
            self.service_product_id.message_post_with_view(
                'meta_vtech_service_product_received_done.track_service_product_line_done_qty',
                values={'line': self, 'done_qty': new_qty},
                subtype_id=self.env.ref('mail.mt_note').id
            )


    # def write(self, vals):
    #     res = super(ServiceProductLine, self).write(vals)
    #     if vals.get("done_qty"):
    #
    #         display_msg = """ The done quantity has been updated. """ + str(vals.get("done_qty")) + """
    #                                                   <br/>
    #                                                   <b>Edited By :</b> """ + self.env.user.partner_id.name + """
    #                                                   <br/>
    #                                               """
    #         self.service_product_id.message_post(body=display_msg)
    #     return res


    # https://www.cybrosys.com/blog/how-to-post-a-message-in-chatter

    # def button_validate(self):
    #     res = super(StockPicking, self).button_validate()
    #     for pick in self:
    #         warehouse_id = pick.picking_type_id.warehouse_id
    #         if warehouse_id and warehouse_id.delivery_steps == 'pick_ship':
    #             for move in pick.move_ids_without_package:
    #                 if move.product_uom_qty != move.quantity_done:
    #                     sale_order = self.env[
    #                         'sale.order'].search([])
    #                     for sl_order in sale_order:
    #                         if sl_order.name == pick.origin:
    #                             sale_order = sl_order
    #                             responsible_person = sale_order.user_id.name
    #                             break
    #                     display_msg = """ Dear """ + responsible + """,
    #                                       <br/>
    #                                       Please find the delivery deviation from
    #                                       the """ + sale_order.name + """
    #                                       <br/>
    #                                       <b>Missing Products:</b>
    #                                       <br/>
    #                                   """
    #                     for prod in move:
    #                         if prod.quantity_done == 0:
    #                             prod_id = self.env[
    #                                 'product.product'].browse(
    #                                 prod['product_id'])
    #                             display_msg += """ - """
    #                             display_msg += str(prod_id.id.name)
    #                             display_msg += """ <br/> """
    #                     sale_order.message_post(body=display_msg)
    #     return res

