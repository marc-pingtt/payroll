from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class td4EditWizard(models.TransientModel):
    _name = 'td4.edit'
    _description = 'TD4 Report'

    year = fields.Char(string='year')
    name = fields.Char(string='Name')
    employee_name = fields.Char(string='Employee Name')
    employee_address = fields.Char(string='Employee Address')
    employer_name = fields.Char(string='Employer Name')
    employer_address = fields.Char(string='Employer Address')
    employee_bir_number = fields.Char(string="Employee's BIR File Number")
    employee_nis_number = fields.Char(string="Employee's NIS Number")
    employer_paye_number = fields.Char(string="Employer's PAYE File Number")
    employer_bir_number = fields.Char(string="Employer's BIR File Number")
    total_deductions = fields.Float(string='Total Deductions as per TD1')
    week_employed = fields.Float(string='Weeks Employed')
    remuneration_before = fields.Float(string='Remuneration before Deduction')
    commissions = fields.Float(string='Commissions')
    taxable_allowance = fields.Float(string='Taxable Allowance')
    travel_allowance = fields.Float(string='Travelling Allowances')
    other_allowance = fields.Float(string='Other Allowances')
    income_relate_previous = fields.Float(string='Income relating to previous year(s) paid in current year')
    saving_plan = fields.Float(string='Saving Plan Withdrawals of Contributions made by company')
    gross_earnings = fields.Float(string='GROSS EARNINGS')
    employer_contribution = fields.Float(string="Employer's Contribution to Approved Fund Contract")
    travel_dispensation = fields.Float(string='Travelling-Dispensation Only')
    employee_contribution = fields.Float(string="Employee's contribution to Company's Approved Pension Fund Plan/Scheme")
    nis_deduction = fields.Float(string='National Insurance Deducted')
    paye_deduction = fields.Float(string='Income Tax Deducted (PAYE)')
    no_of_weeks_health = fields.Float(string='Number of Weeks for which Health Surcharge was Deducted')
    no_of_weeks_at_8_25 = fields.Float(string='Number of Weeks at $8.25')
    no_of_weeks_at_4_80 = fields.Float(string='Number of Weeks at $4.80')
    health_deductions = fields.Float(string='Health Surcharge Deducted')
