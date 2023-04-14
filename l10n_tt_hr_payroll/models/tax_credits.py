from odoo import api, fields, models

class TaxCredit(models.Model):
    _name = "tax.credits"
    _description = "Tax Credits"

    currency_id = fields.Many2one('res.currency', string="Currency", compute="compute_currency_id")
    name = fields.Char("Name", required=True)
    amount = fields.Monetary("Amount")
    type = fields.Many2one(comodel_name="tax.credits.type", required=True, string="Type")
    contract_id = fields.Many2one(comodel_name="hr.contract", required=True, string="Contract")
    year_valid_from = fields.Date("Date From", required=True)
    year_valid_to = fields.Date("Date To")

    @api.depends('contract_id')
    def compute_currency_id(self):
        self.currency_id = self.contract_id.currency_id.id


class TaxCreditType(models.Model):
    _name = "tax.credits.type"
    _description = "Tax Credit Type"

    currency_id = fields.Many2one('res.currency', string='Account Currency')
    name = fields.Char("Name")
    rule_parameter_ids = fields.Many2many(comodel_name="hr.rule.parameter", string="Rule Parameter ID")