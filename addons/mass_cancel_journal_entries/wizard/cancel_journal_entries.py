# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import api, models, _
from odoo.exceptions import ValidationError

class CancelJournalEntries(models.TransientModel):
    _name = 'cancel.journal.entries'
    _description = "Cancel Journal Entries"

    def cancel_journal_entries(self):
        """ cancel multiple journal entries from the tree view."""
        account_move_recs = self.env['account.move'].browse(
            self._context.get('active_ids'))
        state_list_count  = len(account_move_recs.mapped('state'))
        cancel_list_count = account_move_recs.mapped('state').count('cancel')
        if cancel_list_count == state_list_count:
            raise ValidationError(_('Selected Entries Already Cancelled'))
        else:
            account_move_recs.button_cancel()
        return True
