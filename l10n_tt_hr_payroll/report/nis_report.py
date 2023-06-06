from odoo import models, _
from datetime import datetime


class NisReport(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.monthly_nis_report'

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
            'nis_report_data': self.nis_report_data(data),
        }
        return res

    def nis_report_data(self, data):
        values = []
        main_lines = []
        lines = []
        amount = 0.0
        emp_count = 0
        total_contribution = 0.0
        res_config_details = self.env['ir.config_parameter'].sudo()
        nis_maximum_age = res_config_details.get_param('l10n_tt_hr_payroll.nis_maximum_age')
        nis_minimum_age = res_config_details.get_param('l10n_tt_hr_payroll.nis_minimum_age')
        nis_rates = self.env['nis.rates'].search([], limit=1)
        employees = self.env['hr.employee'].search([])
        payslips = self.env['hr.payslip'].search([])
        date_start = datetime.strptime(data['date_start'], '%Y-%m-%d')
        date_end = datetime.strptime(data['date_end'], '%Y-%m-%d')
        days = abs(date_start.date() - date_end.date()).days
        weeks = round(days / 7)

        if data['employee_ids']:
            employees_select = employees.filtered(lambda x: x.id in data['employee_ids'])
            for employee in employees_select:
                payslip_latest = payslips.filtered(lambda x: x.employee_id == employee)[-1]
                emp_count += 1
                if str(employee.age) and employee.contract_id.wage:
                    for line in nis_rates.nis_line_ids:
                        monthly_earn = line.monthly_earnings.split()
                        if nis_minimum_age and nis_maximum_age:
                            if nis_minimum_age < str(employee.age) < nis_maximum_age:
                                if monthly_earn[2] != 'over':
                                    if float(monthly_earn[0]) <= employee.contract_id.wage <= float(monthly_earn[2]):
                                        amount = line.employees_weekly_contri
                                    elif employee.contract_id.wage > float(monthly_earn[2]):
                                        amount = float(line.employees_weekly_contri)

                        else:
                            if nis_rates.nis_minimum_age < str(employee.age) < nis_rates.nis_maximum_age:
                                if str(monthly_earn[2]) != 'over':
                                    if float(monthly_earn[0]) < employee.contract_id.wage < float(monthly_earn[2]):
                                        amount = line.employees_weekly_contri
                                    elif employee.contract_id.wage > float(monthly_earn[2]):
                                        amount = line.employees_weekly_contri

                    total_contribution_week = float(amount) * weeks
                    total_contribution += round(total_contribution_week, 2)
                    emp_tuple = (employee, amount, round(total_contribution_week, 2), payslip_latest.date_from.year,
                                 payslip_latest.date_from.month, payslip_latest.date_from.day)
                    main_lines.append(emp_tuple)
            employee_count = (emp_count, round(total_contribution, 2))
            lines.append(employee_count)

        else:
            for employee in employees:
                payslip = payslips.filtered(lambda x: x.employee_id == employee)
                if payslip:
                    payslip_latest = payslip[-1]
                    emp_count += 1
                    if str(employee.age) and employee.contract_id.wage:
                        for line in nis_rates.nis_line_ids:
                            monthly_earn = line.monthly_earnings.split()
                            if nis_minimum_age and nis_maximum_age:
                                if nis_minimum_age < str(employee.age) < nis_maximum_age:
                                    if monthly_earn[2] != 'over':
                                        if float(monthly_earn[0]) <= employee.contract_id.wage <= float(monthly_earn[2]):
                                            amount = line.employees_weekly_contri
                                        elif employee.contract_id.wage > float(monthly_earn[2]):
                                            amount = line.employees_weekly_contri
                            else:
                                if nis_rates.nis_minimum_age < str(employee.age) < nis_rates.nis_maximum_age:
                                    if str(monthly_earn[2]) != 'over':
                                        if float(monthly_earn[0]) < employee.contract_id.wage < float(monthly_earn[2]):
                                            amount = line.employees_weekly_contri
                                        elif employee.contract_id.wage > float(monthly_earn[2]):
                                            amount = line.employees_weekly_contri
                    else:
                        for line in nis_rates.nis_line_ids:
                            monthly_earn = line.monthly_earnings.split()
                            if monthly_earn[2] != 'over':
                                if float(monthly_earn[0]) <= employee.contract_id.wage <= float(monthly_earn[2]):
                                    amount = line.employees_weekly_contri
                                elif employee.contract_id.wage > float(monthly_earn[2]):
                                    amount = line.employees_weekly_contri
                    total_contribution_week = float(amount) * weeks
                    total_contribution += total_contribution_week
                    emp_tuple = (employee, amount, round(total_contribution_week, 2), payslip_latest.date_from.year,
                                 payslip_latest.date_from.month, payslip_latest.date_from.day)
                    main_lines.append(emp_tuple)
            employee_count = (emp_count, round(total_contribution, 2))
            lines.append(employee_count)
        values.append({
            'main_lines': main_lines,
            'lines': lines,
            'weeks': weeks,
        })
        return values
