# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, pool):
    """
    Fetches all the purchase request and resets the sequence of the purchase request lines
    """
    env = Environment(cr, SUPERUSER_ID, {})
    sale = env["comparison"].search([])
    sale._reset_sequence()
