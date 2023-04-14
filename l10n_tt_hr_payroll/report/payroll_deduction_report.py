from odoo import models, _


class SummaryReport(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.monthly_payroll_deduction_report'

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

    def summary_report_data(self, data):
        categories = self.env['hr.salary.rule'].search([('category_id.id', '=', self.env.ref('hr_payroll.DED').id)])
        employees = self.env['hr.employee'].browse(data['employee_ids'])
        category = []
        for deduct in categories:
            category.append(deduct)
        payslip_lines = self.env['hr.payslip.line'].search(
            [('employee_id', 'in', data['employee_ids']), ('category_id.id', '=', self.env.ref('hr_payroll.DED').id)])
        lines = []
        category_lst = []
        values = []
        total_amt = 0.0
        if employees:
            for cat in category:
                for line in payslip_lines:
                    if str(line.date_from.month) == data['month'] and str(line.date_from.year) == data['year'] and line.code == cat.code:
                        total_amt += abs(line.total)
                        lines.append(line)
                category_lst.extend([{
                    'cat': cat,
                    'amount': round(total_amt, 2)
                }])
                total_amt = 0.0

        else:

            pay_slip_lines = self.env['hr.payslip.line'].search([
                 ('category_id.id', '=', self.env.ref('hr_payroll.DED').id)])
            for cat in category:
                for line in pay_slip_lines:
                    if str(line.date_from.month) == data['month'] and str(line.date_from.year) == data['year'] and line.code == cat.code:
                        total_amt += abs(line.total)
                        lines.append(line)
                category_lst.extend([{
                    'cat': cat,
                    'amount': round(total_amt, 2)
                }])
                total_amt = 0.0
        values.append({
            'category': category_lst,
            'lines': lines,
        })
        return values
