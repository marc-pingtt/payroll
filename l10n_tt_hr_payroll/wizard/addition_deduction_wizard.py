from odoo import api, fields, models, _
from datetime import datetime, timedelta


class AddDedWizard(models.TransientModel):
    _name = 'additions.deductions.wizard'
    _description = 'Addition Report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    year = fields.Selection([(str(y), str(y)) for y in range(1990, datetime.now().year + 1)], 'Year', required=True)
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                             ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                             ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month',
                             required=True)

    def additions_report(self):
        print(self.month, 'poiuytrew3456789')
        print(dict(self._fields['month'].selection).get(self.month), 'poiuytrew3456789')
        month_name = dict(self._fields['month'].selection).get(self.month)
        data = {'employee_ids': self.employee_ids.ids, 'year': self.year, 'month': self.month, 'month_name': month_name}
        return self.env.ref('payroll_reports.payroll_addition_report').report_action(self.employee_ids, data=data)

    def deductions_report(self):
        data = {'employee_ids': self.employee_ids.ids, 'year': self.year, 'month': self.month}
        return self.env.ref('payroll_reports.payroll_deduction_report').report_action(self.employee_ids, data=data)
