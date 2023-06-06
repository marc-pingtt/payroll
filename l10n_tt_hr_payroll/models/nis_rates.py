from odoo import api, fields, models, _


class NISRates(models.Model):
    _name = 'nis.rates'
    _description = 'NIS Rates'
    _rec_name = 'id'

    nis_deductible_percentage = fields.Integer('% Deductible')
    nis_maximum_age = fields.Integer('Maximum Age')
    nis_minimum_age = fields.Integer('Minimum Age')
    nis_employee_gl_account_number = fields.Many2one(
        'account.account', 'Employee Acc No')
    nis_employer_gl_account_number = fields.Many2one(
        'account.account', 'Employer Acc No')
    nis_show_full_salary = fields.Boolean('Show Full Salary')
    nis_line_ids = fields.One2many('nis.rates.lines', 'line_id')


class NISRatesLines(models.Model):
    _name = 'nis.rates.lines'
    _description = 'NIS Rates Lines'

    line_id = fields.Many2one('nis.rates')
    earnings_class = fields.Char('Earnings Class')
    weekly_earnings = fields.Char('Weekly Earnings')
    monthly_earnings = fields.Char('Monthly Earnings')
    avg_weekly_earnings = fields.Char('Assumed Average Weekly Earnings')
    employees_weekly_contri = fields.Char('Employees Weekly Contribution')
    employers_weekly_contri = fields.Char('Employers Weekly Contribution')
    total_weekly_contri = fields.Char('Total Weekly Contribution')
    class_weekly = fields.Char('Class Z Weekly')
