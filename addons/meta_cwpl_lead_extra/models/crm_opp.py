# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class customLead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    
    def _action_convert(self):
        res = super()._action_convert()
        lead_opp=self.env['crm.lead'].browse(self._context.get('active_ids', []))        
        lead_opp.write({'stage_id':2})
        return res