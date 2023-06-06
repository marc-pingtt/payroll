from odoo import models


class MonthlyPayrollReport(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.monthly_payroll_summary_report'

    def _get_report_values(self, docids, data):
        docs = self.env['hr.employee'].search([
            ('id', 'in', data['employee_ids'])])
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
        total_nis_summary = 0.0
        other_deduction_summary = 0.0
        gross_summary = 0.0
        category_alw_summary = 0.0
        basic_summary = 0.0
        total_deduction_dept_summary = 0.0
        total_summary = 0.0
        employee_count_total = 0
        total = 0.0
        if data['employee_ids']:
            employees_select = employees.filtered(lambda x: x.id in data['employee_ids'])
            for department in departments:
                total_paye_amount = 0.0
                total_basic = 0.0
                total_hsur_amount = 0.0
                total_nis_amount = 0.0
                total_amount = 0.0
                employee_count = 0
                employee_paye_count = 0
                employee_hsur_count = 0
                category_total = 0.0
                gross_total = 0.0
                other_total_deduction = 0.0
                total_deduction_dept = 0.0
                total = 0.0
                for employee in employees_select:
                    other_deduction = 0.0
                    gross_amount = 0.0
                    category_alw_total_amt = 0.0

                    payslip_id = payslip.filtered(
                        lambda x: str(x.date_from.month) == data['month'] and str(x.date_from.year) == data['year'] and x.
                        employee_id.id == employee.id and department == employee.department_id)
                    pay_lines = payslip.line_ids.filtered(
                        lambda x: str(x.date_from.month) == data['month'] and str(x.date_from.year) == data['year'] and x.
                        employee_id.id == employee.id and department == employee.department_id)
                    if pay_lines:
                        deduction_lines = pay_lines.filtered(
                            lambda x: x.category_id == self.env.ref(
                                'hr_payroll.DED') and x.code not in (self.env.ref('l10n_tt_hr_payroll.hr_rule_paye').
                                                                     code, self.env.
                                                                     ref('l10n_tt_hr_payroll.hr_rule_health_surcharge').
                                                                     code, self.env.
                                                                     ref('l10n_tt_hr_payroll.hr_rule_nis').code))
                        for deduction in deduction_lines:
                            other_deduction += abs(deduction.total)
                        paye_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_paye').code)
                        total_paye_amount += abs(paye_rate_lines.total)
                        hsur_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_health_surcharge')
                            .code)
                        nis_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_nis')
                            .code)
                        total_nis_amount += abs(nis_rate_lines.total)
                        category_alw = pay_lines.filtered(
                            lambda x: x.category_id == self.env.ref(
                                'hr_payroll.ALW'))
                        category_gross = pay_lines.filtered(
                            lambda x: x.category_id == self.env.ref(
                                'hr_payroll.GROSS'))
                        gross_amount += abs(category_gross.total)
                        total_hsur_amount += abs(hsur_rate_lines.total)
                        total_deduction = other_deduction + abs(hsur_rate_lines.total) + abs(
                            paye_rate_lines.total) + abs(nis_rate_lines.total)
                        total_amount = total_paye_amount + total_hsur_amount
                        for category in category_alw:
                            category_alw_total_amt += abs(category.total)
                        net_total = gross_amount - total_deduction
                        sub_line_tuple = (employee, payslip_id.date_from, category_alw_total_amt, gross_amount,
                                          abs(nis_rate_lines.total), abs(hsur_rate_lines.total),
                                          abs(paye_rate_lines.total), other_deduction, total_deduction, net_total)
                        lines.append(sub_line_tuple)
                        employee_count += 1
                        if paye_rate_lines.total != 0:
                            employee_paye_count += 1
                        if hsur_rate_lines.total != 0:
                            employee_hsur_count += 1

                        total_basic += employee.contract_id.wage
                        category_total += category_alw_total_amt
                        gross_total += gross_amount
                        other_total_deduction += other_deduction
                        total += net_total
                        total_deduction_dept += total_deduction
                department_tuple = (department, total_basic, category_total, gross_total, total_nis_amount,
                                    total_hsur_amount, total_paye_amount, other_total_deduction,
                                    round(total_deduction_dept, 2), total_amount, employee_count, round(total, 2))
                main_lines.append(department_tuple)
                total_hsur_summary += total_hsur_amount
                total_paye_summary += total_paye_amount
                total_nis_summary += total_nis_amount
                other_deduction_summary += other_total_deduction
                gross_summary += gross_total
                category_alw_summary += category_total
                basic_summary += total_basic
                total_deduction_dept_summary += total_deduction_dept
                total_summary += total
                employee_count_total += employee_count
            total_lines_tuple = (round(basic_summary, 2), round(category_alw_summary, 2), round(gross_summary, 2),
                                 round(other_deduction_summary, 2), round(total_nis_summary, 2),
                                 round(total_hsur_summary, 2), round(total_paye_summary, 2),
                                 round(total_deduction_dept_summary, 2), round(total_summary, 2), employee_count_total)
            summary_lines.append(total_lines_tuple)

        else:
            for department in departments:
                total_paye_amount = 0.0
                total_basic = 0.0
                total_hsur_amount = 0.0
                total_nis_amount = 0.0
                total_amount = 0.0
                employee_count = 0
                employee_paye_count = 0
                employee_hsur_count = 0
                category_total = 0.0
                gross_total = 0.0
                other_total_deduction = 0.0
                total_deduction_dept = 0.0
                total = 0.0
                for employee in employees:
                    other_deduction = 0.0
                    gross_amount = 0.0
                    category_alw_total_amt = 0.0

                    payslip_id = payslip.filtered(lambda x: str(x.date_from.month) == data['month'] and str(x.date_from.year) == data['year'] and x.
                                                  employee_id.id == employee.id and department == employee.
                                                  department_id)
                    pay_lines = payslip.line_ids.filtered(
                        lambda x: str(x.date_from.month) == data['month'] and str(x.date_from.year) == data['year'] and x.
                        employee_id.id == employee.id and department == employee.department_id)
                    if pay_lines:
                        deduction_lines = pay_lines.filtered(
                            lambda x: x.category_id == self.env.ref(
                                'hr_payroll.DED') and x.
                            code not in (self.env.ref('l10n_tt_hr_payroll.hr_rule_paye').code,
                                         self.env.ref('l10n_tt_hr_payroll.hr_rule_health_surcharge').code,
                                         self.env.ref('l10n_tt_hr_payroll.hr_rule_nis').code))
                        for deduction in deduction_lines:
                            other_deduction += abs(deduction.total)
                        paye_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_paye').code)
                        total_paye_amount += abs(paye_rate_lines.total)
                        hsur_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_health_surcharge')
                            .code)
                        nis_rate_lines = pay_lines.filtered(
                            lambda x: x.code == self.env.ref(
                                'l10n_tt_hr_payroll.hr_rule_nis')
                            .code)
                        total_nis_amount += abs(nis_rate_lines.total)
                        category_alw = pay_lines.filtered(
                            lambda x: x.category_id == self.env.ref(
                                'hr_payroll.ALW'))
                        category_gross = pay_lines.filtered(
                            lambda x: x.category_id == self.env.ref(
                                'hr_payroll.GROSS'))
                        gross_amount += abs(category_gross.total)
                        total_hsur_amount += abs(hsur_rate_lines.total)
                        total_deduction = other_deduction + abs(hsur_rate_lines.total) + abs(
                            paye_rate_lines.total) + abs(nis_rate_lines.total)
                        total_amount = total_paye_amount + total_hsur_amount
                        for category in category_alw:
                            category_alw_total_amt += abs(category.total)
                        net_total = gross_amount - total_deduction
                        sub_line_tuple = (employee, payslip_id.date_from, category_alw_total_amt, gross_amount,
                                          abs(nis_rate_lines.total), abs(hsur_rate_lines.total),
                                          abs(paye_rate_lines.total), other_deduction, total_deduction, net_total)
                        lines.append(sub_line_tuple)
                        employee_count += 1
                        if paye_rate_lines.total != 0:
                            employee_paye_count += 1
                        if hsur_rate_lines.total != 0:
                            employee_hsur_count += 1

                        total_basic += employee.contract_id.wage
                        category_total += category_alw_total_amt
                        gross_total += gross_amount
                        other_total_deduction += other_deduction
                        total += net_total
                        total_deduction_dept += total_deduction
                department_tuple = (department, total_basic, category_total, gross_total, total_nis_amount,
                                    total_hsur_amount, total_paye_amount, other_total_deduction,
                                    round(total_deduction_dept, 2), total_amount, employee_count, round(total, 2))
                main_lines.append(department_tuple)
                total_hsur_summary += total_hsur_amount
                total_paye_summary += total_paye_amount
                total_nis_summary += total_nis_amount
                other_deduction_summary += other_total_deduction
                gross_summary += gross_total
                category_alw_summary += category_total
                basic_summary += total_basic
                total_deduction_dept_summary += total_deduction_dept
                # total_deduction_dept_summary += total_deduction_dept
                total_summary += total
                employee_count_total += employee_count
            total_lines_tuple = (round(basic_summary, 2), round(category_alw_summary, 2), round(gross_summary, 2),
                                 round(other_deduction_summary, 2), round(total_nis_summary, 2),
                                 round(total_hsur_summary, 2), round(total_paye_summary, 2),
                                 round(total_deduction_dept_summary, 2), round(total_summary, 2), employee_count_total)
            summary_lines.append(total_lines_tuple)

        values.append({
            'main_lines': main_lines,
            'lines': lines,
            'summary_lines': summary_lines,
            'total': total,
        })
        return values
