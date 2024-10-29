# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLeadLostExtend(models.TransientModel):
    _inherit="crm.lead.lost"
    
    lst_to=fields.Many2one(comodel_name="res.partner",string="Lost To",domain="[ ('category_id.name', 'ilike', 'Competitor')]")
    
    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        return leads.action_set_lost(lost_reason=self.lost_reason_id.id,lost_to=self.lst_to.id)