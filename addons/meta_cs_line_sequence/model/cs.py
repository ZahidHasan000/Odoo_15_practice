# -*- coding: utf-8 -*-

from odoo import api, fields, models


class customCS(models.Model):
    _inherit = "comparison"

    @api.depends("select_product_ids")
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in sale order lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new sale order lines, the sequence is automatically
        added as :  max_sequence + 1
        """
        for cs in self:
            cs.max_line_sequence = max(cs.mapped("select_product_ids.sequence") or [0]) + 1

    max_line_sequence = fields.Integer(
        string="Max sequence in lines", compute="_compute_max_line_sequence", store=True
    )

    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in sorted(rec.select_product_ids, key=lambda x: (x.sequence, x.id)):
                if line.sequence != current_sequence:
                    line.sequence = current_sequence
                current_sequence += 1

    def write(self, line_values):
        res = super(customCS, self).write(line_values)
        self._reset_sequence()
        return res

    def copy(self, default=None):
        return super(customCS, self.with_context(keep_line_sequence=True)).copy(
            default
        )


class customCSLine(models.Model):
    _inherit = "select.po.products"

    # re-defines the field to change the default
    sequence = fields.Integer(
        help="Gives the sequence of this line when displaying the CS Line.",
        default=9999,
    )

    # displays sequence on the line
    sequence2 = fields.Integer(
        help="Shows the sequence of this line in the CS LINE.",
        related="sequence",
        string="SL",
        readonly=True,
        store=True,
    )

    @api.model
    def create(self, values):
        line = super(customCSLine, self).create(values)
        # We do not reset the sequence if we are copying a complete sale order
        if self.env.context.get("keep_line_sequence"):
            line.request_id._reset_sequence()
        return line
