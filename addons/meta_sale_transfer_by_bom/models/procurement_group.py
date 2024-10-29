
import logging
from collections import defaultdict, namedtuple

from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, _, api, fields, models, registry
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero, html_escape
from odoo.tools.misc import split_every


class ProcurementGroupInherit(models.Model):
    _inherit = 'procurement.group'

    Procurementbom = namedtuple('Procurementbom', ['product_id', 'product_qty', 'bom_id',
                                             'product_uom', 'location_id', 'name', 'origin', 'company_id', 'values'])

    # if line.bom_id:
    #     procurements.append(self.env['procurement.group'].Procurementbom(
    #         line.product_id, product_qty, line.bom_id, procurement_uom,
    #         line.order_id.partner_shipping_id.property_stock_customer,
    #         line.product_id.display_name, line.order_id.name, line.order_id.company_id, values))
    # else:
    #     procurements.append(self.env['procurement.group'].Procurement(
    #         line.product_id, product_qty, procurement_uom,
    #         line.order_id.partner_shipping_id.property_stock_customer,
    #         line.product_id.display_name, line.order_id.name, line.order_id.company_id, values))