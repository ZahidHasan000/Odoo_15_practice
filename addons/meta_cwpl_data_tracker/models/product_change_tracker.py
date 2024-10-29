# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CwplProductDataTracker(models.Model):
    _inherit = 'product.template'
    
    
    name = fields.Char('Name', index=True, required=True, translate=True, tracking=True)
    description = fields.Html('Description', translate=True, tracking=True)
    description_purchase = fields.Text('Purchase Description', translate=True,tracking=True)
    description_sale = fields.Text('Sales Description', tracking=True, translate=True,help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note")
    detailed_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type',tracking=True, default='consu', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    list_price = fields.Float(
        'Sales Price', tracking=True,default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.",
    )
    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price',tracking=True, groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")

    sale_ok = fields.Boolean('Can be Sold', default=True,tracking=True)
    purchase_ok = fields.Boolean('Can be Purchased', default=True,tracking=True)
    uom_name = fields.Char(string='Unit of Measure Name', related='uom_id.name', readonly=True,tracking=True)

    default_code = fields.Char(
        'Product Code', compute='_compute_default_code',
        inverse='_set_default_code', store=True,tracking=True)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Favorite'),
    ], default='0', string="Favorite",tracking=True)