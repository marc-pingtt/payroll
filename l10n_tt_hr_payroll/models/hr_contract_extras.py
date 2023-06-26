from odoo import api, fields, models

class OtherIncomeSources(models.Model):
    _name = "other.income.sources"
    _description = "Other Income Sources"

    currency_id = fields.Many2one('res.currency', string="Currency", compute="compute_currency_id")
    name = fields.Char("Name", required=True)
    amount = fields.Monetary("Amount")
    contract_id = fields.Many2one(comodel_name="hr.contract", required=False, string="Contract")
    year_valid_from = fields.Date("Date From", required=True)
    year_valid_to = fields.Date("Date To")
    is_weekly =  fields.Boolean("Is Additions Weekly?")

    @api.depends('contract_id')
    def compute_currency_id(self):
        self.currency_id = self.contract_id.currency_id.id