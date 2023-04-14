from odoo import api, fields, models, _

class HrContract(models.Model):
    _inherit = "hr.contract"

    tax_deductions = fields.One2many(comodel_name="tax.deductions", inverse_name="contract_id")
    tax_credits = fields.One2many(comodel_name="tax.credits", inverse_name="contract_id")
    salary_additions = fields.One2many(comodel_name="salary.additions", inverse_name="contract_id")
    prior_earnings = fields.Monetary(name="prior_earnings")
    prior_nis_paid = fields.Monetary(name="prior_nis_paid")
    prior_paye_paid = fields.Monetary(name="prior_paye_paid")
    prior_hsur_paid = fields.Monetary(name="prior_hsur_paid")