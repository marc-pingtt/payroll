from odoo import models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SummaryReport(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.summary_report'

    # @api.model
    def _get_report_values(self, docids, data):
        docs = self.env['hr.employee'].search([])
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'data': data,
            'summary_report_data': self.summary_report_data(data),
        }

    def summary_report_data(self, data):
        total_remuneration = 0.0
        total_commissions = 0.0
        taxable_travel = 0.0
        previous_year_income = 0.0
        other_taxable_allowances = 0.0
        total_benefits = 0.0
        total_gross_earnings = 0.0
        non_taxable_travel = 0.0
        other_non_taxable_allowances = 0.0
        other_before_deductions = 0.0
        total_before_tax_pension = 0.0
        total_after_tax_pension = 0.0
        total_nis = 0.0
        total_health_surcharge = 0.0
        total_paye = 0.0
        allowances = 0.0
        employer_contributions = 0.0
        no_of_non_paye_employees = 0
        no_of_paye_employees = 0
        no_of_non_hsur_employees = 0
        no_of_hsur_employees = 0
        no_of_non_nis_employees = 0
        no_of_nis_employees = 0
        gross_of_non_taxable_employees = 0.0
        employees = self.env['hr.employee'].search([])
        no_of_employees = self.env['hr.employee'].search_count([])
        company = self.env.company
        res_config_details = self.env['ir.config_parameter'].sudo()
        # personal_deduction = res_config_details.get_param('l10n_tt_hr_payroll.paye_personal_deduction')
        # health_surcharge_minimum_age = res_config_details.get_param('l10n_tt_hr_payroll.health_surcharge_minimum_age')
        # health_surcharge_maximum_age = res_config_details.get_param('l10n_tt_hr_payroll.health_surcharge_maximum_age')
        # nis_maximum_age = res_config_details.get_param('l10n_tt_hr_payroll.nis_maximum_age')
        # nis_minimum_age = res_config_details.get_param('l10n_tt_hr_payroll.nis_minimum_age')
        personal_deduction = 0.0
        health_surcharge_minimum_age = 16
        health_surcharge_maximum_age = 70
        nis_maximum_age = 65
        nis_minimum_age = 18
        employee = self.env['hr.employee'].search([('id', 'in', data['employee_ids'])])
        if employee:
            for rec in employee:
                emp_annual_salary = rec.contract_id.wage * 12
                if emp_annual_salary < float(personal_deduction):
                    no_of_non_paye_employees += 1

                else:
                    no_of_paye_employees += 1
                if health_surcharge_minimum_age < int(str(rec.age)) < health_surcharge_maximum_age:
                    no_of_hsur_employees += 1
                else:
                    no_of_non_hsur_employees += 1
                if nis_minimum_age < int(str(rec.age)) < nis_maximum_age:
                    no_of_nis_employees += 1
                else:
                    no_of_non_nis_employees += 1
                payslip = self.env['hr.payslip'].search([('state', '!=', 'cancel'), ('employee_id', '=', rec.id)])
                if payslip:
                    total_remuneration += rec.contract_id.wage * 12
                    for line in payslip.line_ids:

                        if line.code == 'TA' and str(line.date_from.year) == (data['year']):
                            taxable_travel += line.total
                        elif line.code != 'TA':
                            other_taxable_allowances += line.total
                        # if line.code == 'BASIC' and str(line.date_from.year) == str(year):
                        #     basic_salary += line.total
                        if line.code == 'PAYE' and str(line.date_from.year) == (data['year']):
                            total_paye += line.total
                        if line.code == 'HSLR' and str(line.date_from.year) == (data['year']):
                            total_health_surcharge += line.total
                        if line.code == 'NIS' and str(line.date_from.year) == (data['year']):
                            total_nis += line.total
                        if line.category_id.code == 'ALW' and str(line.date_from.year) == (data['year']):
                            allowances += line.total
                        # if line.category_id.code == 'DED' and str(line.date_from.year) == str(year):
                        #     deductions += line.total
                    total_gross_earnings += (rec.contract_id.wage * 12) + allowances

            values = {
                'total_remuneration': round(total_remuneration, 2),
                'taxable_travel': round(taxable_travel, 2),
                'other_taxable_allowances': round(other_taxable_allowances, 2),
                'total_paye': round(abs(total_paye), 2),
                'total_health_surcharge': round(abs(total_health_surcharge), 2),
                'total_nis': round(abs(total_nis), 2),
                'total_gross_earnings': round(total_gross_earnings, 2),
                'company_name': company.name,
                'no_of_employees': no_of_employees,
                'no_of_non_paye_employees': no_of_non_paye_employees,
                'no_of_paye_employees': no_of_paye_employees,
                'no_of_non_hsur_employees': no_of_non_hsur_employees,
                'no_of_hsur_employees': no_of_hsur_employees,
                'no_of_non_nis_employees': no_of_non_nis_employees,
                'no_of_nis_employees': no_of_nis_employees,
                'gross_of_non_taxable_employees': allowances,
                'total_commissions': total_commissions,
                'previous_year_income': previous_year_income,
                'total_benefits': total_benefits,
                'non_taxable_travel': non_taxable_travel,
                'other_non_taxable_allowances': other_non_taxable_allowances,
                'other_before_deductions': other_before_deductions,
                'total_before_tax_pension': total_before_tax_pension,
                'total_after_tax_pension': total_after_tax_pension,
                'employer_contributions': employer_contributions,

            }
        else:
            for employee in employees:
                emp_annual_salary = employee.contract_id.wage*12
                if emp_annual_salary < float(personal_deduction):
                    no_of_non_paye_employees += 1
                else:
                    no_of_paye_employees += 1
                if health_surcharge_minimum_age < str(employee.age) < health_surcharge_maximum_age:
                    no_of_hsur_employees += 1
                else:
                    no_of_non_hsur_employees += 1
                if nis_minimum_age < str(employee.age) < nis_maximum_age:
                    no_of_nis_employees += 1
                else:
                    no_of_non_nis_employees += 1
                payslip = self.env['hr.payslip'].search([('state', '!=', 'cancel'), ('employee_id', '=', employee.id)])
                if payslip:
                    total_remuneration += employee.contract_id.wage * 12
                    for line in payslip.line_ids:
                        if line.code == 'TA' and str(line.date_from.year) == (data['year']):
                            taxable_travel += line.total
                        elif line.code != 'TA':
                            other_taxable_allowances += line.total
                        if line.code == 'PAYE' and str(line.date_from.year) == (data['year']):
                            total_paye += line.total
                        if line.code == 'HSLR'and str(line.date_from.year) == (data['year']):
                            total_health_surcharge += line.total
                        if line.code == 'NIS'and str(line.date_from.year) == (data['year']):
                            total_nis += line.total
                        if line.category_id.code == 'ALW' and str(line.date_from.year) == (data['year']):
                            allowances += line.total
                        # if line.category_id.code == 'DED' and str(line.date_from.year) == str(year):
                        #     deductions += line.total
                    total_gross_earnings += (employee.contract_id.wage * 12) + allowances

            values = {
                'total_remuneration': round(total_remuneration, 2),
                'taxable_travel': round(taxable_travel, 2),
                'other_taxable_allowances': round(other_taxable_allowances, 2),
                'total_paye': round(abs(total_paye), 2),
                'total_health_surcharge': round(abs(total_health_surcharge), 2),
                'total_nis': round(abs(total_nis), 2),
                'total_gross_earnings': round(total_gross_earnings, 2),
                'company_name': company.name,
                'no_of_employees': no_of_employees,
                'no_of_non_paye_employees': no_of_non_paye_employees,
                'no_of_paye_employees': no_of_paye_employees,
                'no_of_non_hsur_employees': no_of_non_hsur_employees,
                'no_of_hsur_employees': no_of_hsur_employees,
                'no_of_non_nis_employees': no_of_non_nis_employees,
                'no_of_nis_employees': no_of_nis_employees,
                'gross_of_non_taxable_employees': allowances,
                'total_commissions': total_commissions,
                'previous_year_income': previous_year_income,
                'total_benefits': total_benefits,
                'non_taxable_travel': non_taxable_travel,
                'other_non_taxable_allowances': other_non_taxable_allowances,
                'other_before_deductions': other_before_deductions,
                'total_before_tax_pension': total_before_tax_pension,
                'total_after_tax_pension': total_after_tax_pension,
                'employer_contributions': employer_contributions,

            }
        return values
