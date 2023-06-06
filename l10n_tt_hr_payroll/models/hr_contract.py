from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = "hr.contract"

    tax_deductions = fields.One2many(
        comodel_name="tax.deductions", inverse_name="contract_id")
    tax_credits = fields.One2many(
        comodel_name="tax.credits", inverse_name="contract_id")
    salary_additions = fields.One2many(
        comodel_name="salary.additions", inverse_name="contract_id")
    prior_earnings = fields.Monetary(name="prior_earnings")
    prior_nis_paid = fields.Monetary(name="prior_nis_paid")
    prior_paye_paid = fields.Monetary(name="prior_paye_paid")
    prior_hsur_paid = fields.Monetary(name="prior_hsur_paid")
    is_pension = fields.Boolean(name="Pension")
    year_of_prior_validity = fields.Date(name="Year of Prior Validity")
    other_income_sources = fields.One2many(
        comodel_name="other.income.sources", inverse_name="contract_id")
    is_nis_untaxed = fields.Boolean(name="NIS Untaxed?", default=False)
    ignore_hsur = fields.Boolean(name="Ignore HSUR?", default=False)

    def get_valid_other_income_sources(self, date):
        return self.other_income_sources.filtered(lambda x: x.year_valid_from <= date and (x.year_valid_to is False or x.year_valid_to >= date))

    def get_valid_other_income_sources_date_range(self, date_from, date_to):
        return self.other_income_sources.filtered(lambda x: x.year_valid_from <= date_to and (x.year_valid_to is False or x.year_valid_to >= date_from))
