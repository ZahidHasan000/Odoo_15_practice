from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta
from odoo.http import Controller, request, route


class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
                                 compute="_compute_journal_id",
                                 domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")

    @api.depends('can_edit_wizard', 'company_id')
    def _compute_journal_id(self):
        for wizard in self:
            journal = wizard.env['account.journal'].sudo().search([('name', '=', 'Select')], limit=1)
            if journal:
                batch = wizard._get_batches()[0]
                jrnl_id = wizard._get_batch_journal(batch)
                wizard.journal_id = journal.id
            else:
                # wizard.journal_id = self.env['account.journal'].search([
                #     ('type', 'in', ('bank', 'cash')),
                #     ('company_id', '=', wizard.company_id.id),
                # ], limit=1)
                wizard.journal_id = False