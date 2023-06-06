from odoo import models, fields


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    default_schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
        ('daily', 'Daily')
    ], string='Default Scheduled Pay', default='monthly',
        help="Defines the frequency of the wage payment.")


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
        ('daily', 'Daily')
    ], compute='_compute_schedule_pay', store=True, readonly=False,
        string='Scheduled Pay', index=True,
        help="Defines the frequency of the wage payment.")
