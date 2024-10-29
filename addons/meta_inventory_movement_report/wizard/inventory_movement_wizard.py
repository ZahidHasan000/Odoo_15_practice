# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
from itertools import groupby
import json
from datetime import date, datetime, timedelta


class InventoryMovementWizard(models.TransientModel):
    _name = 'inventory.movement.wizard'
    _description = 'Inventory Movement Wizard'

    def _default_company_id(self):
        # company = self.env['res.company'].sudo().search([('name', '=', 'Aristo Food Exporter Limited')], limit=1)
        company = self.env.company.id
        return company

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self._default_company_id())
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    report_type = fields.Selection([
        ("location_wise", "Location Wise all Product"),
        ("product_wise_all_location", "Product Wise all Location"),
        ("product_wise_details", "Product Wise Details"),
    ], string="Type", default="location_wise")

    product_typ = fields.Selection([
        ("all_product", "All Product"),
        ("specific_product", "Specific Product")], string="Product Type", default="all_product")

    category = fields.Many2one('product.category', string='Category')

    product_id = fields.Many2one('product.product', string="Product",
                                 domain="[('categ_id', '=', category)]")

    product_id2 = fields.Many2one('product.product', string="Product",
                                 domain="[('detailed_type', '=', 'product')]")
    product2_categ_id = fields.Many2one('product.category', related="product_id2.categ_id", string="Category")

    location_id = fields.Many2one('stock.location', string="Location",
                                  domain=["&", ('usage', '=', 'internal'), ('location_id.usage', '=', 'view')])

    # @api.onchange('category')
    # def return_categ_product(self):
    #     for rec in self:
    #         if rec.category:
    #             return {'domain': {'product_id': [('categ_id', '=', rec.category.id)]}}

    def get_product_ids(self):
        product_ids = []
        if self.category and not self.product_id:
            domain = ["&", ('company_id', '=', self.company_id.id), ('categ_id', '=', self.category.id)]
            product_ids.extend(self.env['product.product'].sudo().search(domain).mapped('id'))

        elif self.product_id:
            product_ids.extend(self.env['product.product'].sudo().search([('id', '=', self.product_id.id)]).mapped('id'))

        product_ids = list(set(product_ids))
        return product_ids

    def action_apply_report(self):
        if self.start_date and self.end_date:
            if self.report_type == 'location_wise':
                self._cr.execute('TRUNCATE TABLE location_wise_product_data')

                opening_date_form = self.start_date - timedelta(days=1)
                opening_date_form2 = str(opening_date_form) + ' ' + '23:59:59'
                from_date = str(self.start_date) + ' ' + '00:00:00'
                to_date = str(self.end_date) + ' ' + '23:59:59'

                products = self.env['product.product'].sudo().browse(self.get_product_ids())
                for product in products:
                    opening_in_moves = self.env['stock.move.line'].sudo().search([
                        ('product_id', '=', product.id),
                        ('date', '<', opening_date_form2),
                        ['state', '=', 'done'],
                        ['location_dest_id', '=', self.location_id.id]
                    ])
                    opening_out_moves = self.env['stock.move.line'].sudo().search([
                        ('product_id', '=', product.id),
                        ('date', '<', opening_date_form2),
                        ['state', '=', 'done'],
                        ['location_id', '=', self.location_id.id]
                    ])

                    date_range_in_moves = self.env['stock.move.line'].sudo().search([
                        ('product_id', '=', product.id),
                        ('date', '>', from_date),
                        ('date', '<', to_date),
                        ['state', '=', 'done'],
                        ['location_dest_id', '=', self.location_id.id]
                    ])

                    date_range_out_moves = self.env['stock.move.line'].sudo().search([
                        ('product_id', '=', product.id),
                        ('date', '>', from_date),
                        ('date', '<', to_date),
                        ['state', '=', 'done'],
                        ['location_id', '=', self.location_id.id]
                    ])

                    open_in_qty = self._compute_input_quantity_for_opening(
                        opening_in_moves,
                        in_usages=['internal', 'inventory', 'supplier', 'production', 'customer']
                    )
                    open_out_qty = self._compute_output_quantity_for_opening(
                        opening_out_moves,
                        dest_usages=['internal', 'inventory', 'supplier', 'production', 'customer']
                    )

                    date_range_in_qty = self._compute_input_quantity_date_range(
                        date_range_in_moves,
                        in_usages=['internal', 'inventory', 'supplier', 'production', 'customer']
                    )
                    date_range_out_qty = self._compute_output_quantity_for_date_range(
                        date_range_out_moves,
                        dest_usages=['internal', 'inventory', 'supplier', 'production', 'customer']
                    )
                    open_qty = open_in_qty - open_out_qty
                    closing_qty = open_qty + (date_range_in_qty - date_range_out_qty)
                    self.env['location.wise.product.data'].create({
                        'product_id': product.id,
                        'product_uom_id': product.uom_id.id,
                        'product_categ_id': product.categ_id.id,
                        'opening_quantity': open_qty,
                        'date_range_in_quantity': date_range_in_qty,
                        'date_range_out_quantity': date_range_out_qty,
                        'closing_quantity': closing_qty,
                    })
                search_product_data = self.env['location.wise.product.data'].sudo().search_read([])
                # driver_adv_data = self.env['driver.advance.data'].search_read([])

                data = {
                    'form_data': self.read()[0],
                    'product_item': search_product_data,
                }

                return self.env.ref('meta_inventory_movement_report.location_wise_product_report1').report_action(self, data=data)
            else:
                raise UserError(_('Please Select Start Date and End Date First !'))
    def _compute_input_quantity_for_opening(self, move_lines, in_usages=[]):
        return sum(
            line.product_uom_id._compute_quantity(
                line.qty_done, line.product_id.uom_id)
            for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.state == 'done')
        )
    def _compute_output_quantity_for_opening(self, move_lines, dest_usages=[]):
        return sum(
            line.product_uom_id._compute_quantity(
                line.qty_done, line.product_id.uom_id)
            for line in move_lines.filtered(lambda l: l.location_dest_id.usage in dest_usages and l.state == 'done')
        )

    def _compute_input_quantity_date_range(self, move_lines, in_usages=[]):
        return sum(
            line.product_uom_id._compute_quantity(
                line.qty_done, line.product_id.uom_id)
            for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.state == 'done')
        )
    def _compute_output_quantity_for_date_range(self, move_lines, dest_usages=[]):
        return sum(
            line.product_uom_id._compute_quantity(
                line.qty_done, line.product_id.uom_id)
            for line in move_lines.filtered(lambda l: l.location_dest_id.usage in dest_usages and l.state == 'done')
        )

    def get_all_internal_location_ids(self):
        location_ids = []
        if self.report_type == 'product_wise_all_location':
            domain = ["&", "&", ('usage', '=', 'internal'), ('location_id.usage', '=', 'view'),
                      ('company_id', '=', self.company_id.id)]
            location_ids.extend(self.env['stock.location'].sudo().search(domain).mapped('id'))

        location_ids = list(set(location_ids))
        return location_ids

    def action_apply_report_all_location(self):
        if self.start_date and self.end_date:
            if self.report_type == 'product_wise_all_location':
                self._cr.execute('TRUNCATE TABLE product_wise_location_data')

                opening_date_form = self.start_date - timedelta(days=1)
                opening_date_form2 = str(opening_date_form) + ' ' + '23:59:59'
                from_date = str(self.start_date) + ' ' + '00:00:00'
                to_date = str(self.end_date) + ' ' + '23:59:59'

                locations = self.env['stock.location'].sudo().browse(self.get_all_internal_location_ids())
                for location in locations:
                    opening_in_moves = self.env['stock.move.line'].sudo().search([
                        ('product_id', '=', self.product_id2.id),
                        ('date', '<', opening_date_form2),
                        ['state', '=', 'done'],
                        ['location_dest_id', '=', location.id]
                    ])
                    opening_out_moves = self.env['stock.move.line'].sudo().search([
                        ('product_id', '=', self.product_id2.id),
                        ('date', '<', opening_date_form2),
                        ['state', '=', 'done'],
                        ['location_id', '=', location.id]
                    ])

                    date_range_in_moves = self.env['stock.move.line'].sudo().search([
                        ('product_id', '=', self.product_id2.id),
                        ('date', '>', from_date),
                        ('date', '<', to_date),
                        ['state', '=', 'done'],
                        ['location_dest_id', '=', location.id]
                    ])

                    date_range_out_moves = self.env['stock.move.line'].sudo().search([
                        ('product_id', '=', self.product_id2.id),
                        ('date', '>', from_date),
                        ('date', '<', to_date),
                        ['state', '=', 'done'],
                        ['location_id', '=', location.id]
                    ])

                    open_in_qty = self._compute_input_quantity_for_opening(
                        opening_in_moves,
                        in_usages=['internal', 'inventory', 'supplier', 'production', 'customer']
                    )
                    open_out_qty = self._compute_output_quantity_for_opening(
                        opening_out_moves,
                        dest_usages=['internal', 'inventory', 'supplier', 'production', 'customer']
                    )

                    date_range_in_qty = self._compute_input_quantity_date_range(
                        date_range_in_moves,
                        in_usages=['internal', 'inventory', 'supplier', 'production', 'customer']
                    )
                    date_range_out_qty = self._compute_output_quantity_for_date_range(
                        date_range_out_moves,
                        dest_usages=['internal', 'inventory', 'supplier', 'production', 'customer']
                    )

                    open_qty = open_in_qty - open_out_qty
                    closing_qty = open_qty + (date_range_in_qty - date_range_out_qty)
                    self.env['product.wise.location.data'].create({
                        'location_id': location.id,
                        'product_uom_id': self.product_id2.uom_id.id,
                        'opening_quantity': open_qty,
                        'date_range_in_quantity': date_range_in_qty,
                        'date_range_out_quantity': date_range_out_qty,
                        'closing_quantity': closing_qty,
                    })

                search_location_data = self.env['product.wise.location.data'].sudo().search_read([])

                data = {
                    'form_data': self.read()[0],
                    'location_item': search_location_data,
                }

                return self.env.ref('meta_inventory_movement_report.location_wise_product_report2').report_action(self,
                                                                                                              data=data)
            else:
                raise UserError(_('Please Select Start Date and End Date First !'))

    def action_report_product_details_data(self):
        if self.start_date and self.end_date:
            opening_date_form = self.start_date - timedelta(days=1)
            opening_date_form2 = str(opening_date_form) + ' ' + '23:59:59'
            from_date = str(self.start_date) + ' ' + '00:00:00'
            to_date = str(self.end_date) + ' ' + '23:59:59'

            self.env['product.stock.data'].sudo().search([]).unlink()
            self.env['product.stock.data.line'].sudo().search([]).unlink()

            list_item1 = []
            for item1 in self.product_id2:
                opening_products_move = self.env['stock.move'].sudo().search([
                    ('company_id', '=', self.company_id.id),
                    ('product_id', '=', item1.id),
                    ('create_date', '<', opening_date_form2),
                    ['state', '=', 'done'],
                ])

                in_usages1 = ['supplier', 'customer', 'inventory', 'production'],
                dest_usages1 = ['internal']
                in_usages2 = ['internal'],
                dest_usages2 = ['supplier', 'customer', 'inventory', 'production']
                in_qty1 = 0.0
                in_value1 = 0.0
                out_qty1 = 0.0
                out_value1 = 0.0

                for opn_in_qty1 in opening_products_move.filtered(lambda l: l.location_id.usage in ['internal', 'supplier', 'customer', 'inventory', 'production'] and l.location_dest_id.usage in ['internal']):
                    opn_qty_count1 = opn_in_qty1.product_uom._compute_quantity(opn_in_qty1.quantity_done,
                                                                                  opn_in_qty1.product_id.uom_id)

                    in_qty1 += opn_qty_count1
                    cost_open = opn_in_qty1.product_id.uom_id._compute_price(opn_in_qty1.product_id.with_company(self.company_id).standard_price, opn_in_qty1.product_id.uom_id)
                    if opn_in_qty1.purchase_line_id:
                        opn_in_price1 = opn_in_qty1.purchase_line_id.price_unit
                    elif opn_in_qty1.sale_line_id:
                        opn_in_price1 = opn_in_qty1.sale_line_id.price_unit
                    elif opn_in_qty1.production_id:
                        opn_in_price1 = opn_in_qty1.production_id.selling_price
                    elif opn_in_qty1.selling_price > 0.0:
                        opn_in_price1 = opn_in_qty1.selling_price
                    else:
                        opn_in_price1 = cost_open

                    in_value1 += opn_qty_count1 * opn_in_price1
                for opn_out_qty1 in opening_products_move.filtered(
                        lambda l: l.location_id.usage in ['internal'] and l.location_dest_id.usage in ['internal', 'supplier', 'customer', 'inventory', 'production']):
                    opn_qty_count2 = opn_out_qty1.product_uom._compute_quantity(opn_out_qty1.quantity_done,
                                                                                  opn_out_qty1.product_id.uom_id)
                    out_qty1 += opn_qty_count2
                    cost_out = opn_out_qty1.product_id.list_price
                    if opn_out_qty1.purchase_line_id:
                        opn_out_price1 = opn_out_qty1.purchase_line_id.price_unit
                    elif opn_out_qty1.sale_line_id:
                        opn_out_price1 = opn_out_qty1.sale_line_id.price_unit
                    elif opn_out_qty1.production_id:
                        opn_out_price1 = opn_out_qty1.production_id.selling_price
                    elif opn_out_qty1.selling_price > 0.0:
                        opn_out_price1 = opn_out_qty1.selling_price
                    else:
                        opn_out_price1 = cost_out

                    out_value1 += opn_qty_count2 * opn_out_price1

                self.env['product.stock.data'].create({
                    'product_id': item1.id,
                    'product_uom': item1.uom_id.id,
                    'product_category': item1.categ_id.id,
                    'opening_in_qty': in_qty1,
                    'opening_out_qty': out_qty1,
                    'cost_price': in_value1 / in_qty1,
                    'sales_price': out_value1 / out_qty1,
                })

            product_record_data = self.env['product.stock.data'].sudo().search([])

            for record in product_record_data:

                date_range_move = self.env['stock.move'].sudo().search([
                    ('company_id', '=', self.company_id.id),
                    ('product_id', '=', record.product_id.id),
                    ('create_date', '>', from_date),
                    ('create_date', '<', to_date),
                    ['state', '=', 'done'],
                ])
                in_sorch_usages = ['supplier', 'customer', 'inventory', 'production']
                in_dest_usages = ['internal']
                out_source_usages = ['internal']
                out_dest_usages = ['supplier', 'customer', 'inventory', 'production']

                for in_qty in date_range_move.filtered(
                        lambda l: l.location_id.usage in ['internal', 'supplier', 'customer', 'inventory', 'production'] and l.location_dest_id.usage in ['internal']):
                    date_range_in_quantity = in_qty.product_uom._compute_quantity(in_qty.quantity_done,
                                                                                  in_qty.product_id.uom_id)
                    cost = in_qty.product_id.uom_id._compute_price(in_qty.product_id.with_company(self.company_id).standard_price, in_qty.product_id.uom_id)

                    if in_qty.purchase_line_id:
                        price = in_qty.purchase_line_id.price_unit
                    elif in_qty.sale_line_id:
                        price = in_qty.sale_line_id.price_unit
                    elif in_qty.production_id:
                        price = in_qty.production_id.selling_price
                    elif in_qty.selling_price > 0.0:
                        price = in_qty.selling_price
                    else:
                        price = cost

                    self.env['product.stock.data.line'].create({
                        'product_data': record.id,
                        'date_time': in_qty.create_date,
                        'date': in_qty.date,
                        'in_quantity': date_range_in_quantity,
                        'in_rate': price,
                    })

                for out_qty in date_range_move.filtered(
                        lambda l: l.location_id.usage in ['internal'] and l.location_dest_id.usage in ['internal', 'supplier', 'customer', 'inventory', 'production']):
                    date_range_out_quantity = out_qty.product_uom._compute_quantity(out_qty.quantity_done,
                                                                                    out_qty.product_id.uom_id)

                    if out_qty.sale_line_id:
                        price_out = out_qty.sale_line_id.price_unit
                    elif out_qty.purchase_line_id:
                        price_out = out_qty.purchase_line_id.price_unit
                    elif out_qty.production_id:
                        price_out = out_qty.production_id.selling_price
                    elif out_qty.selling_price > 0.0:
                        price_out = out_qty.selling_price
                    else:
                        price_out = record.product_id.list_price

                    self.env['product.stock.data.line'].create({
                        'product_data': record.id,
                        'date_time': out_qty.create_date,
                        'date': out_qty.date,
                        'out_quantity': date_range_out_quantity,
                        'out_price': price_out,
                    })

            self.print_report_data()
            search_data = self.env['product.stock.data'].sudo().search([])
            data = {
                'form_data': self.read()[0],
                'product_item': search_data.read(),
                'product_line_item': search_data.item_line_ids.read(),
            }

            return self.env.ref('meta_inventory_movement_report.location_wise_product_report3').report_action(self, data)

    def _compute_open_input_quantity_from_move_lines(self, move_lines, in_usages=[], dest_usages=[]):
        return sum(
            line.product_uom._compute_quantity(
                line.quantity_done, line.product_id.uom_id)
            for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.location_dest_id.usage in dest_usages and l.state == 'done')
        )

    def _compute_open_output_quantity_from_move_lines(self, move_lines, in_usages=[], dest_usages=[]):
        return sum(
            line.product_uom._compute_quantity(
                line.quantity_done, line.product_id.uom_id)
            for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.location_dest_id.usage in dest_usages and l.state == 'done')
        )

    def print_report_data(self):
        product_data = self.env['product.stock.data'].sudo().search([])
        for item2 in product_data:
            final_opn_quantity = sum(line.in_quantity for line in item2.item_line_ids) + item2.opening_in_qty
            final_out_quantity = sum(line.out_quantity for line in item2.item_line_ids) + item2.opening_out_qty
            item2.open_final_total = final_opn_quantity
            item2.out_final_total = final_out_quantity

            opn_final_rate1 = (item2.opening_in_qty * item2.cost_price) + sum(line11.in_quantity * line11.in_rate for line11 in item2.item_line_ids)
            out_final_rate1 = (item2.opening_out_qty * item2.sales_price) + sum(line22.out_quantity * line22.out_price for line22 in item2.item_line_ids)

            print(opn_final_rate1, out_final_rate1)
            item2.opn_final_rate = opn_final_rate1 / final_opn_quantity
            item2.out_final_rate = out_final_rate1 / final_out_quantity

            final_opening_qty = item2.opening_in_qty - item2.opening_out_qty

            date_range_product_data = self.env['product.stock.data.line'].sudo().search([])
            for data_line in date_range_product_data:
                total = data_line.in_quantity - data_line.out_quantity
                final_opening_qty += total

                data_line.balance = final_opening_qty
                data_line.in_value = data_line.in_quantity * data_line.in_rate
                data_line.out_value = data_line.out_quantity * data_line.out_price


    # def open_in_purchase_value(self, move_lines, in_usages=[], dest_usages=[]):
    #     return sum(line.quantity_done*line.purchase_line_id.price_unit
    #         for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.location_dest_id.usage in dest_usages and l.state == 'done' and l.purchase_line_id)
    #     )
    #
    # def open_in_return_value(self, move_lines, in_usages=[], dest_usages=[]):
    #     return sum(line.quantity_done*line.sale_line_id.price_unit
    #         for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.location_dest_id.usage in dest_usages and l.state == 'done' and l.sale_line_id)
    #     )
    #
    # def open_in_production_value(self, move_lines, in_usages=[], dest_usages=[]):
    #     return sum(line.quantity_done*line.production_id.selling_price
    #         for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.location_dest_id.usage in dest_usages and l.state == 'done' and l.production_id)
    #     )
    #
    # def open_in_production_value2(self, move_lines, in_usages=[], dest_usages=[]):
    #     return sum(line.quantity_done*line.selling_price
    #         for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.location_dest_id.usage in dest_usages and l.state == 'done' and l.selling_price > 0.0)
    #     )
    # def open_in_value(self, move_lines, in_usages=[], dest_usages=[], cost=0.0):
    #     return sum(line.quantity_done*cost
    #         for line in move_lines.filtered(lambda l: l.location_id.usage in in_usages and l.location_dest_id.usage in dest_usages and l.state == 'done'
    #                                                   and not l.selling_price > 0.0 and not l.production_id and not l.sale_line_id and not l.purchase_line_id)
    #     )