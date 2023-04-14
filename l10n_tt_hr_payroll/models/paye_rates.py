from odoo import api, fields, models, _


class PayeRates(models.Model):
    _name = 'paye.rates'
    _description = 'Paye Rates'
    _rec_name = 'id'

    paye_personal_deduction = fields.Float('Personal Deduction')
    paye_senior_citizen_deduction = fields.Float('Senior Citizen Deduction ')
    paye_mortgage_limit = fields.Float('Mortgage Limit')
    paye_tertiary_education_limit = fields.Float('Tertiary Education Limit')
    paye_account_number = fields.Many2one('account.account', 'Account No')
    paye_senior_citizen_age = fields.Integer('Senior Citizen Age')
    paye_alimony_limit = fields.Float('Alimony limit')
    paye_other_annuities_limit = fields.Float('Other Annuities limit')
