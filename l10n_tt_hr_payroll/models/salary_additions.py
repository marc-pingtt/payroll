from odoo import api, fields, models


class SalaryAddition(models.Model):
    _name = "salary.additions"
    _description = "Salary Additions"

    currency_id = fields.Many2one(
        'res.currency', string="Currency", compute="compute_currency_id")
    name = fields.Char("Name", required=True)
    amount = fields.Monetary("Amount")
    type = fields.Many2one(
        comodel_name="salary.additions.type", required=True, string="Type")
    contract_id = fields.Many2one(
        comodel_name="hr.contract", required=False, string="Contract")
    year_valid_from = fields.Date("Date From", required=True)
    year_valid_to = fields.Date("Date To")

    @api.depends('contract_id')
    def compute_currency_id(self):
        self.currency_id = self.contract_id.currency_id.id


class TaxCreditType(models.Model):
    _name = "salary.additions.type"
    _description = "Salary Additions Type"

    currency_id = fields.Many2one('res.currency', string='Account Currency')
    name = fields.Char("Name")
