# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
from itertools import groupby
import json
from datetime import date, datetime, timedelta


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[
        ('draft', 'User'),
        ('waiting',),
        ('confirmed',),
        ('assigned',),
        ('done',),
        ('commissioned', 'Commissioned'),
        ('cancel',),
    ], default='draft',
        ondelete={'draft': 'cascade', 'waiting': 'cascade', 'confirmed': 'cascade', 'assigned': 'cascade', 'done': 'cascade',
                  'commissioned': 'cascade', 'cancel': 'cascade'})

    def action_commissioning_date(self):
        for rec in self:
            rec.write({
                'do_com_date':(datetime.now()).date(),
                'state': 'commissioned'
            })