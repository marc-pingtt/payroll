from odoo import api, fields, models, _


class HealthSurchargeRates(models.Model):
    _name = 'health.surcharge.rates'
    _description = 'Health Surcharge Rates'
    _rec_name = 'id'

    health_surcharge_minimum_age = fields.Integer('Minimum Age')
    health_surcharge_maximum_age = fields.Integer('Maximum Age')
    health_surcharge_account_number = fields.Many2one(
        'account.account', 'Account No')
    health_line_ids = fields.One2many(
        'health.surcharge.rates.lines', 'health_id')


class HealthSurchargeRatesLines(models.Model):
    _name = 'health.surcharge.rates.lines'
    _description = 'Health Surcharge Rates'
    _rec_name = 'id'

    health_id = fields.Many2one('health.surcharge.rates')
    min_emoluments = fields.Monetary('Minimum Emoluments')
    max_emoluments = fields.Monetary('Maximum Emoluments')
    rate = fields.Monetary('Rate')
