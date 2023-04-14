from odoo import models


class TaxReport(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.monthly_tax_report'

    def _get_report_values(self, docids, data):
        docs = self.env['hr.employee'].search([('id', 'in', data['employee_ids'])])
        company = self.env.company
        res = {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'data': data,
            'company': company,
            'docs': docs,
            'summary_report_data': self.summary_report_data(data),
        }
        return res

    def summary_report_data(self, data):
        employees = self.env['hr.employee'].search([])
        payslip = self.env['hr.payslip'].search([])
        departments = self.env['hr.department'].search([])
        main_lines = []
        values = []
        lines = []
        summary_lines = []
        total_paye_summary = 0.0
        total_hsur_summary = 0.0
        total = 0.0
        if data['employee_ids']:
            employees_select = employees.filtered(lambda x: x.id in data['employee_ids'])
            for department in departments:
                total_paye_amount = 0.0
                total_hsur_amount = 0.0
                total_amount = 0.0
                employee_count = 0
                employee_paye_count = 0
                employee_hsur_count = 0
                for employee in employees_select:
                    pay_lines = payslip.line_ids.filtered(
                        lambda x: str(x.date_from.month) == data['month'] and str(x.date_from.year) == data[
                            'year'] and x.
                                  employee_id.id == employee.id and department == employee.department_id)
                    if pay_lines:
                        paye_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_paye').code)
                        total_paye_amount += abs(paye_rate_lines.total)
                        hsur_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_health_surcharge')
                            .code)
                        total_hsur_amount += abs(hsur_rate_lines.total)
                        sub_total = abs(paye_rate_lines.total) + abs(
                            hsur_rate_lines.total)
                        total_amount = total_paye_amount + total_hsur_amount
                        sub_line_tuple = (employee, abs(paye_rate_lines.total),
                                          abs(hsur_rate_lines.total), sub_total)
                        lines.append(sub_line_tuple)
                        employee_count += 1
                        if paye_rate_lines.total != 0:
                            employee_paye_count += 1
                        if hsur_rate_lines.total != 0:
                            employee_hsur_count += 1
                        total_paye_summary += total_paye_amount
                        total_hsur_summary += total_hsur_amount
                        total = total_paye_summary + total_hsur_summary
                department_tuple = (department, total_paye_amount,
                                    total_hsur_amount, total_amount, employee_count,
                                    employee_paye_count, employee_hsur_count)
                main_lines.append(department_tuple)
            summary_lines_tuple = (total_paye_summary, total_hsur_summary)
            summary_lines.append(summary_lines_tuple)
        else:
            for department in departments:
                total_paye_amount = 0.0
                total_hsur_amount = 0.0
                total_amount = 0.0
                employee_count = 0
                employee_paye_count = 0
                employee_hsur_count = 0
                for employee in employees:
                    payslip_id = payslip.filtered(lambda x: str(x.date_from.month) == data['month'] and x.
                                                  employee_id.id == employee.id and department == employee.
                                                  department_id)
                    pay_lines = payslip.line_ids.filtered(
                        lambda x: str(x.date_from.month) == data['month'] and str(x.date_from.year) == data[
                            'year'] and x.
                                  employee_id.id == employee.id and department == employee.department_id)
                    if pay_lines:
                        paye_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_paye').code)
                        total_paye_amount += abs(paye_rate_lines.total)
                        hsur_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_health_surcharge')
                            .code)
                        total_hsur_amount += abs(hsur_rate_lines.total)
                        sub_total = abs(paye_rate_lines.total) + abs(
                            hsur_rate_lines.total)
                        total_amount = total_paye_amount + total_hsur_amount
                        sub_line_tuple = (employee, abs(paye_rate_lines.total),
                                          abs(hsur_rate_lines.total), sub_total)
                        lines.append(sub_line_tuple)
                        employee_count += 1
                        if paye_rate_lines.total != 0:
                            employee_paye_count += 1
                        if hsur_rate_lines.total != 0:
                            employee_hsur_count += 1
                        total_paye_summary += total_paye_amount
                        total_hsur_summary += total_hsur_amount
                        total = total_paye_summary + total_hsur_summary
                department_tuple = (department, total_paye_amount,
                                    total_hsur_amount, total_amount, employee_count,
                                    employee_paye_count, employee_hsur_count)
                main_lines.append(department_tuple)
            summary_lines_tuple = (total_paye_summary, total_hsur_summary)
            summary_lines.append(summary_lines_tuple)
        values.append({
            'main_lines': main_lines,
            'lines': lines,
            'total_paye_summary': total_paye_summary,
            'total_hsur_summary': total_hsur_summary,
            'total': total,
        })
        return values
