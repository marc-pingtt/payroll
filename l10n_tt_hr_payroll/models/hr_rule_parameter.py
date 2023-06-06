from odoo import api, fields, models

class HrRuleParameter(models.Model):
    _inherit = "hr.rule.parameter"

    tax_deduction_type_id = fields.Many2one(comodel_name="tax.deduction.type")