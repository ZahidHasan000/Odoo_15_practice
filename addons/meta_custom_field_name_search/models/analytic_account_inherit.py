# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import ValidationError


class AccountAnalyticInherit(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', '|', ('name', operator, name), ('code', operator, name),
                     ('partner_id', operator, name)]
        print('***---****---***', name_get_uid)
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)