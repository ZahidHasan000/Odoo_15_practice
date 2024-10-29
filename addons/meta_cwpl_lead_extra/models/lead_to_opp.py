# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class customLead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    
    def action_apply(self):
        res = super().action_apply()
        lead_opp=self.env['crm.lead'].browse(self._context.get('active_ids', []))        
        lead_opp.write({'stage_id':2,'lead_status':'accepted'})
        return res
    
    # def _action_convert(self):
    #     res = super()._action_convert()
    #     lead_opp=self.env['crm.lead'].browse(self._context.get('active_ids', []))        
    #     lead_opp.write({'stage_id':2})
    #     return res
    
    