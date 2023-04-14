from odoo import models, _
from datetime import date


class SummaryReportAdd(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.monthly_payroll_addition_report'

    def _get_report_values(self, docids, data):
        docs = self.env['hr.employee'].search([('id', 'in', data['employee_ids'])])
        company = self.env.company
        res = {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'data': data,
            'company': company.name,
            'docs': docs,
            'summary_report_data': self.summary_report_data(data),
        }
        return res

    def summary_report_data(self, data, date_from=None):
        codes = self.env['hr.salary.rule'].search([('category_id.id', '=', self.env.ref('hr_payroll.ALW').id)])
        month = int(data['month'])
        # if month == 1:
            # month_
        total_value = 0.0
        lines = []
        values = []
        main_lines = []
        domain = []
        if data['employee_ids']:
            domain.append(('employee_id', 'in', data['employee_ids']))
        payslip = self.env['hr.payslip'].search(domain)
        for code in codes:
            pay_lines = payslip.line_ids.filtered(
                lambda x: x.code == code.code and str(x.date_from.year) == data['year'] and str(
                    x.date_from.month) == data['month'])
            total_alw = 0.0
            for line in pay_lines.mapped('total'):
                total_alw += line
            code_tuple = (code.code, total_alw)
            main_lines.append(code_tuple)
        if data['employee_ids']:
            for employee in self.env['hr.employee'].browse(data['employee_ids']):
                payslip_lines = payslip.line_ids.filtered(lambda x: str(x.date_from.year) == data['year'] and x.
                                                          category_id.id == self.env.ref('hr_payroll.ALW').id and x.
                                                          employee_id.id == employee.id)
                for code in codes:
                    payslip_lines_ytd = payslip_lines.filtered(
                        lambda x: x.code == code.code and x.date_from.month <= month)
                    payslip_lines_month = payslip_lines.filtered(
                        lambda x: x.code == code.code and x.date_from.month == month)
                    amount = payslip_lines_ytd.mapped('total')
                    amount_month = payslip_lines_month.total
                    for value in amount:
                        total_value += value
                    tup = (employee, code.code, amount_month, total_value, payslip_lines_month.date_from)
                    total_value = 0.0
                    lines.append(tup)
        else:
            for employee in self.env['hr.employee'].search([]):
                payslip_lines = payslip.line_ids.filtered(
                    lambda x: str(x.date_from.year) == data['year'] and x.category_id.id == self.env.ref(
                        'hr_payroll.ALW').id and x.employee_id.id == employee.id)
                if payslip_lines:
                    for code in codes:
                        payslip_lines_ytd = payslip_lines.filtered(
                            lambda x: x.code == code.code and x.date_from.month <= month)
                        payslip_lines_month = payslip_lines.filtered(
                            lambda x: x.code == code.code and x.date_from.month == month)
                        amount = payslip_lines_ytd.mapped('total')
                        amount_month = payslip_lines_month.total
                        for value in amount:
                            total_value += value
                        tup = (employee, code.code, amount_month, total_value, payslip_lines_month.date_from)
                        total_value = 0.0
                        lines.append(tup)
        values.append({
            'main_lines': main_lines,
            'lines': lines,
        })
        return values
