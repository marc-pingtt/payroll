from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    nis_maximum_age = fields.Integer(string='Maximum Age', default=15)
    nis_minimum_age = fields.Integer(string='Minimum Age')
    nis_employee_gl_account_number = fields.Many2one(
        'account.account', string='Employee Acc No')
    nis_employer_gl_account_number = fields.Many2one(
        'account.account', 'Employer Acc No')

    paye_personal_deduction = fields.Float(string='Personal Deduction')
    paye_rate = fields.Float(string='PAYE Rate')
    paye_senior_citizen_deduction = fields.Float(
        string='Senior Citizen Deduction ')
    paye_mortgage_limit = fields.Float(string='Mortgage Limit')
    paye_tertiary_education_limit = fields.Float(
        string='Tertiary Education Limit')
    paye_account_number = fields.Many2one(
        'account.account', string='Account No')
    paye_senior_citizen_age = fields.Integer(string='Senior Citizen Age')
    paye_alimony_limit = fields.Float(string='Alimony limit')
    paye_other_annuities_limit = fields.Float(string='Other Annuities limit')

    health_surcharge_minimum_age = fields.Integer(string='Minimum Age')
    health_surcharge_maximum_age = fields.Integer(string='Maximum Age')
    health_surcharge_account_number = fields.Many2one(
        'account.account', string='Account No')

    # # set_values method
    # def set_values(self):
    #     res = super(ResConfigSettings, self).set_values()
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         'l10n_tt_hr_payroll.nis_maximum_age', self.nis_maximum_age)
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         'l10n_tt_hr_payroll.nis_minimum_age', self.nis_minimum_age)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.nis_employee_gl_account_number',
    #                                                      self.nis_employee_gl_account_number)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.nis_employer_gl_account_number',
    #                                                      self.nis_employer_gl_account_number)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.paye_personal_deduction',
    #                                                      self.paye_personal_deduction)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.paye_senior_citizen_deduction',
    #                                                      self.paye_senior_citizen_deduction)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.paye_mortgage_limit',
    #                                                      self.paye_mortgage_limit)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.paye_tertiary_education_limit',
    #                                                      self.paye_tertiary_education_limit)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.paye_account_number',
    #                                                      self.paye_account_number)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.paye_alimony_limit',
    #                                                      self.paye_alimony_limit)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.paye_senior_citizen_age',
    #                                                      self.paye_senior_citizen_age)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.paye_other_annuities_limit',
    #                                                      self.paye_other_annuities_limit)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.health_surcharge_minimum_age',
    #                                                      self.health_surcharge_minimum_age)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.health_surcharge_maximum_age',
    #                                                      self.health_surcharge_maximum_age)
    #     self.env['ir.config_parameter'].sudo().set_param('l10n_tt_hr_payroll.health_surcharge_account_number',
    #                                                      self.health_surcharge_account_number)
    #     return res

    # # get_values method
    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()

    #     nis_deductible_percentage = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.nis_deductible_percentage')
    #     nis_maximum_age = self.env['ir.config_parameter'].sudo(
    #     ).get_param('l10n_tt_hr_payroll.nis_maximum_age')
    #     nis_minimum_age = self.env['ir.config_parameter'].sudo(
    #     ).get_param('l10n_tt_hr_payroll.nis_minimum_age')
    #     nis_employee_gl_account_number = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.nis_employee_gl_account_number')
    #     nis_employer_gl_account_number = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.nis_employer_gl_account_number')
    #     nis_show_full_salary = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.nis_show_full_salary')
    #     paye_personal_deduction = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.paye_personal_deduction')
    #     paye_senior_citizen_deduction = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.paye_senior_citizen_deduction')
    #     paye_mortgage_limit = self.env['ir.config_parameter'].sudo(
    #     ).get_param('l10n_tt_hr_payroll.paye_mortgage_limit')
    #     paye_tertiary_education_limit = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.paye_tertiary_education_limit')
    #     paye_account_number = self.env['ir.config_parameter'].sudo(
    #     ).get_param('l10n_tt_hr_payroll.paye_account_number')
    #     paye_alimony_limit = self.env['ir.config_parameter'].sudo(
    #     ).get_param('l10n_tt_hr_payroll.paye_alimony_limit')
    #     paye_senior_citizen_age = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.paye_senior_citizen_age')
    #     paye_other_annuities_limit = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.paye_other_annuities_limit')
    #     health_surcharge_minimum_age = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.health_surcharge_minimum_age')
    #     health_surcharge_maximum_age = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.health_surcharge_maximum_age')
    #     health_surcharge_account_number = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.health_surcharge_account_number')
    #     health_surcharge_account_number = self.env['ir.config_parameter'].sudo().get_param(
    #         'l10n_tt_hr_payroll.health_surcharge_account_number')
    #     res.update(
    #         nis_deductible_percentage=nis_deductible_percentage,
    #         nis_maximum_age=nis_maximum_age,
    #         nis_minimum_age=nis_minimum_age,
    #         nis_employee_gl_account_number=nis_employee_gl_account_number,
    #         nis_employer_gl_account_number=nis_employer_gl_account_number,
    #         nis_show_full_salary=nis_show_full_salary,
    #         paye_personal_deduction=paye_personal_deduction,
    #         paye_senior_citizen_deduction=paye_senior_citizen_deduction,
    #         paye_mortgage_limit=paye_mortgage_limit,
    #         paye_tertiary_education_limit=paye_tertiary_education_limit,
    #         paye_account_number=paye_account_number,
    #         paye_senior_citizen_age=paye_senior_citizen_age,
    #         paye_alimony_limit=paye_alimony_limit,
    #         paye_other_annuities_limit=paye_other_annuities_limit,
    #         health_surcharge_minimum_age=health_surcharge_minimum_age,
    #         health_surcharge_maximum_age=health_surcharge_maximum_age,
    #         health_surcharge_account_number=health_surcharge_account_number

    #     )
    #     return res
