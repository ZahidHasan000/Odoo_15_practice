
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RepairOrderInherit(models.Model):
    _inherit = 'repair.order'

    state = fields.Selection(selection_add=[
        ('draft', 'User'),
        ('check', 'Checker'),
        ('to_approve', 'Waiting for Approve'),
        ('cross_function', 'Cross Function'),
        ('confirmed',),
        ('ready',),
        ('under_repair',),
        ('2binvoiced',),
        ('done', ),
        ('cancel',)
    ], default='draft',
        ondelete={'draft': 'cascade', 'check': 'cascade', 'to_approve': 'cascade', 'cross_function': 'cascade',
                  'confirmed': 'cascade', 'ready': 'cascade', 'under_repair': 'cascade', '2binvoiced': 'cascade',
                  'done': 'cascade', 'cancel': 'cascade'})

    project_number = fields.Many2one('account.analytic.account', string="Project Number")

    def user_send_quotation_to_check(self):
        for rec in self:
            rec.write({'state': 'check'})

    def user_cancel_quotation(self):
        for rec in self:
            rec.action_repair_cancel()

    def checker_send_quotation_to_approve(self):
        for rec in self:
            rec.write({'state': 'to_approve'})

    def checker_revert_to_draft(self):
        for rec in self:
            rec.action_repair_cancel_draft()

    def checker_cancel_quotation(self):
        for rec in self:
            rec.action_repair_cancel()

    def approve_quotation_and_send_cross_function(self):
        for rec in self:
            rec.write({'state': 'cross_function'})

    def approver_revert_to_draft(self):
        for rec in self:
            rec.action_repair_cancel_draft()

    def approver_cancel_quotation(self):
        for rec in self:
            rec.action_repair_cancel()

    def cross_function_revert_to_draft(self):
        for rec in self:
            rec.action_repair_cancel_draft()

    def cross_function_cancel_quotation(self):
        for rec in self:
            rec.action_repair_cancel()

    def action_repair_confirm(self):
        """ Repair order state is set to 'To be invoiced' when invoice method
        is 'Before repair' else state becomes 'Confirmed'.
        @param *arg: Arguments
        @return: True
        """
        if self.filtered(lambda repair: repair.state != 'cross_function'):
            raise UserError(_("Only cross function repairs can be confirmed."))
        self._check_company()
        self.operations._check_company()
        self.fees_lines._check_company()
        before_repair = self.filtered(lambda repair: repair.invoice_method == 'b4repair')
        before_repair.write({'state': '2binvoiced'})
        to_confirm = self - before_repair
        to_confirm_operations = to_confirm.mapped('operations')
        to_confirm_operations.write({'state': 'confirmed'})
        to_confirm.write({'state': 'confirmed'})
        return True