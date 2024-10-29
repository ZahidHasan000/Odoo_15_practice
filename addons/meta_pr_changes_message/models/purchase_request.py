from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class PurchaseRequestMessage(models.Model):
    _inherit = 'purchase.request'

    def write(self, vals):
        if vals.get('type_of_expenditure'):
            notes = "Type of Expenditure Changes to "
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.type_of_expenditure, 'new_values': vals.get('type_of_expenditure')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('pr_type'):
            notes = "PR Type Changes to "
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.pr_type, 'new_values': vals.get('pr_type')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))
        if vals.get('submitted_by_department'):
            notes = "Submitted By Changes to "
            submitted_by = self.env['hr.department'].browse(vals.get('submitted_by_department'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.submitted_by_department.name, 'new_values': submitted_by.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('order_item'):
            notes = "Sales Order Changes to "
            order = self.env['sale.order'].browse(vals.get('order_item'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.order_item.name, 'new_values': order.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('so_business_product_type'):
            notes = "Business Product Type Changes to "
            # order = self.env['hr.department'].browse(vals.get('order_item'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.so_business_product_type, 'new_values': vals.get('so_business_product_type')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('user_department'):
            notes = "User Department Changes to "
            department = self.env['hr.department'].browse(vals.get('user_department'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.user_department.name, 'new_values': department.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('requisition_type'):
            notes = "Requisition Type Changes to "
            # order = self.env['hr.department'].browse(vals.get('order_item'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.requisition_type, 'new_values': vals.get('requisition_type')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))
        if vals.get('contact_person'):
            notes = "User Department Changes to "
            hr = self.env['hr.employee'].browse(vals.get('contact_person'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.contact_person.name, 'new_values': hr.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('project_number'):
            notes = "Project Number Changes to "
            project = self.env['account.analytic.account'].browse(vals.get('project_number'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.project_number.name, 'new_values': project.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('customer_name'):
            notes = "Customer Name Changes to "
            customer = self.env['res.partner'].browse(vals.get('customer_name'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.customer_name.name, 'new_values': customer.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('assign_to'):
            notes = "Assign To Changes "
            hr = self.env['hr.employee'].browse(vals.get('assign_to'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.assign_to.name, 'new_values': hr.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))
        if vals.get('sales_person'):
            notes = "Sales Person Changes to "
            hr = self.env['hr.employee'].browse(vals.get('sales_person'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.sales_person.name, 'new_values': hr.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('required_by_date'):
            notes = "Required Date Changes to "
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.required_by_date, 'new_values': vals.get('required_by_date')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))
        if vals.get('delivery_location'):
            notes = "Delivery Location Changes to "
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.delivery_location, 'new_values': vals.get('delivery_location')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))
        if vals.get('delivery_location_add'):
            notes = "Delivery Location Address Changes to "
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.delivery_location_add, 'new_values': vals.get('delivery_location_add')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))
        if vals.get('budget_as_per_design'):
            notes = "Budget as per Design Changes to "
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.budget_as_per_design, 'new_values': vals.get('budget_as_per_design')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))
        if vals.get('pr_note'):
            notes = "Note Changes to "
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.pr_note, 'new_values': vals.get('pr_note')},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('cost_head'):
            notes = "Cost Head Changes to "
            cost_head = self.env['cost.head'].browse(vals.get('cost_head'))
            self.message_post_with_view('meta_pr_changes_message.track_pr_form_view_changes',
                                         values={'self': self, 'notes': notes, 'old_values': self.cost_head.name, 'new_values': cost_head.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        return super(PurchaseRequestMessage, self).write(vals)


class PurchaseRequestLineMessage(models.Model):
    _inherit = 'purchase.request.line'

    def write(self, vals):
        if vals.get('sale_order_line'):
            notes = "Sale Order Line "
            sale_line = self.env['sale.order.line'].browse(vals.get('sale_order_line'))
            self.request_id.message_post_with_view('meta_pr_changes_message.track_pr_line_message',
                                         values={'self': self, 'notes': notes, 'old_values': self.sale_order_line.name, 'new_values': sale_line.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('ref_bom_id'):
            notes = "BOM ID "
            bom = self.env['mrp.bom'].browse(vals.get('ref_bom_id'))
            self.request_id.message_post_with_view('meta_pr_changes_message.track_pr_line_message',
                                         values={'self': self, 'notes': notes, 'old_values': self.ref_bom_id.name, 'new_values': bom.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('analytic_account_id'):
            notes = "Cost Center "
            analytic_account = self.env['account.analytic.account'].browse(vals.get('analytic_account_id'))
            self.request_id.message_post_with_view('meta_pr_changes_message.track_pr_line_message',
                                         values={'self': self, 'notes': notes, 'old_values': self.analytic_account_id.name, 'new_values': analytic_account.name},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('product_qty'):
            notes = "Product Quantity "
            self.request_id.message_post_with_view('meta_pr_changes_message.track_pr_line_message',
                                         values={'self': self, 'notes': notes, 'old_values': str(self.product_qty), 'new_values': str(vals.get('product_qty'))},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('average_cost'):
            notes = "Average Cost "
            self.request_id.message_post_with_view('meta_pr_changes_message.track_pr_line_message',
                                         values={'self': self, 'notes': notes, 'old_values': str(self.average_cost), 'new_values': str(vals.get('average_cost'))},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('reserved_qty'):
            notes = "Reserved Quantity "
            self.request_id.message_post_with_view('meta_pr_changes_message.track_pr_line_message',
                                         values={'self': self, 'notes': notes, 'old_values': str(self.reserved_qty), 'new_values': str(vals.get('reserved_qty'))},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('procurement_qty'):
            notes = "Procurement Quantity "
            self.request_id.message_post_with_view('meta_pr_changes_message.track_pr_line_message',
                                         values={'self': self, 'notes': notes, 'old_values': str(self.procurement_qty), 'new_values': str(vals.get('procurement_qty'))},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        if vals.get('estimated_cost'):
            notes = "Estimated Cost "
            self.request_id.message_post_with_view('meta_pr_changes_message.track_pr_line_message',
                                         values={'self': self, 'notes': notes, 'old_values': str(self.estimated_cost), 'new_values': str(vals.get('estimated_cost'))},
                                         subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                             'mail.mt_note'))

        return super(PurchaseRequestLineMessage, self).write(vals)

    # def _track_service_qty_received(self, new_qty):
    #     self.ensure_one()
    #     if new_qty != self.done_qty:
    #         self.service_product_id.message_post_with_view(
    #             'meta_vtech_service_product_received_done.track_service_product_line_done_qty',
    #             values={'line': self, 'done_qty': new_qty},
    #             subtype_id=self.env.ref('mail.mt_note').id
    #         )

# order.message_post_with_view('meta_purchase_comparison_system.track_cs_purchase_order_creation',
#                                                     values={'self': order, 'origin': self},
#                                                     subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
#                                                         'mail.mt_note'))