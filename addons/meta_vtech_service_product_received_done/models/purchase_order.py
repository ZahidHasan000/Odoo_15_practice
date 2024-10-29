from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta


class PurchaseServiceGrn(models.Model):
    _inherit = 'purchase.order'

    service_item_ids = fields.One2many('service.product', 'source_document', string='Service Products Are')

    def button_confirm(self):
        self.create_service_item_list()
        return super().button_confirm()
    
    def create_service_item_list(self):
        for rec in self:
            product_list = []
            print('Joyanto Joyanto Joyanto')
            if any(rec.order_line.product_id.filtered(lambda d: d.detailed_type == 'service')):
                # print('Joyanto2 Joyanto2 Joyanto2')
                for item in rec.order_line.filtered(lambda d: d.product_id.detailed_type == 'service'):
                    purchase_line_values = {
                        'name': item.name,
                        'product': item.product_id.id,
                        'order_qty': item.product_qty,
                        'purchase_order_line_id': item.id,
                    }
                    product_list.append((0, 0, purchase_line_values))

                service = self.env['service.product']
                service.create({
                    'partner_id': rec.partner_id.id,
                    'source_document': rec.id,
                    'product_line': product_list
                    })

    @api.depends('service_item_ids')
    def _compute_service_item_number(self):
        for rec in self:
            rec.services_count = len(rec.service_item_ids)

    services_count = fields.Integer(compute='_compute_service_item_number', )

    def view_services_item(self):
        result = self.env["ir.actions.actions"]._for_xml_id('meta_vtech_service_product_received_done.service_product_po_action')
        # override the context to get rid of the default filtering on operation type
        result['context'] = {'default_partner_id': self.partner_id.id, 'default_source_document': self.id}
        service_ids = self.mapped('service_item_ids')
        # choose the view_mode accordingly
        if not service_ids or len(service_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (service_ids.ids)
        elif len(service_ids) == 1:
            res = self.env.ref('meta_vtech_service_product_received_done.service_product_po_views_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = service_ids.id
        return result

    @api.depends('order_line')
    def check_service_item(self):
        for rec in self:
            if rec.order_line:
                if any(rec.order_line.product_id.filtered(lambda d: d.detailed_type == 'service' and d.name != 'Advance to Supplier')):
                    rec['is_service_item_available'] = True
                else:
                    rec['is_service_item_available'] = False
            else:
                rec['is_service_item_available'] = False

    is_service_item_available = fields.Boolean(compute="check_service_item", string="Is Service Item Available",
                                               default=False)

    def generate_grn(self):
        self.create_service_item_list()
        result = self.env["ir.actions.actions"]._for_xml_id(
            'meta_vtech_service_product_received_done.service_product_po_action')
        # override the context to get rid of the default filtering on operation type
        result['context'] = {'default_partner_id': self.partner_id.id, 'default_source_document': self.id}
        service_ids = self.mapped('service_item_ids')
        # choose the view_mode accordingly
        if not service_ids or len(service_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (service_ids.ids)
        elif len(service_ids) == 1:
            res = self.env.ref('meta_vtech_service_product_received_done.service_product_po_views_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = service_ids.id
        return result
