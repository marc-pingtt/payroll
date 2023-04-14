from odoo import fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime


class NisReportDueWizard(models.TransientModel):
    _name = 'nis.report.due.wizard'
    _description = 'NIS Report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    # year = fields.Selection([(str(y), str(y)) for y in range(1990, datetime.now().year + 1)], 'Year', required=True)
    # month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'arch'), ('4', 'April'),
    #                          ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
    #                          ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month')
    date_start = fields.Date('Start Period', required=True,
                             default=lambda self: (fields.Date.today() - relativedelta(years=0)).replace(month=1,
                                                                                                         day=1),
                             help="Start date of the period to consider.")
    date_end = fields.Date('End Period', required=True,
                           default=lambda self: (fields.Date.today() - relativedelta(years=0)).replace(month=12,
                                                                                                       day=31),
                           help="End date of the period to consider.")

    def print(self):
        data = {'employee_ids': self.employee_ids.ids, 'date_start': self.date_start, 'date_end': self.date_end}
        return self.env.ref('payroll_reports.payroll_nis_report_dues').report_action(self.employee_ids, data=data)
