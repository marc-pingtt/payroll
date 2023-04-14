from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
import calendar
from decimal import Decimal


class payrunReportWizard(models.TransientModel):
    _name = "payrun.report.wizard"
    _description = "Payrun Report"

    report_period_start = fields.Date("Report Period Start", required=True)
    report_period_end = fields.Date("Report Period End")

    @api.onchange("report_period_start")
    def compute_report_period_end(self):
        if (self.report_period_start != False):
            last_day = calendar.monthrange(
                self.report_period_start.year, self.report_period_start.month)[1]
            self.report_period_end = date(
                self.report_period_start.year, self.report_period_start.month, last_day)

    def payslip_search(self, report_period_start, report_period_end):
        domain = [('company_id', '=', self.env.user.company_id.id),
                  ('date_from', '>=', report_period_start),
                  ('date_to', '<=', report_period_end)]
        payslips = self.env['hr.payslip'].search(domain).sudo()
        return payslips

    def print_report(self):
        self.ensure_one()
        payslips_ids = self.payslip_search(
            self.report_period_start, self.report_period_end)
        if not payslips_ids:
            raise UserError(_('No payslips found for the selected period.'))
        payslips = []
        for payslip in payslips_ids:
            payslips.append(payslip.id)

        return self.env.ref('l10n_tt_hr_payroll.payrun_report_action').report_action(self, data={'payslips': payslips,"report_start":self.report_period_start, \
            "report_end":self.report_period_end,"gen_date":self.write_date,"name":self.env.user.display_name,})


class PayrunReport(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.payrun_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        payslips = self.env['hr.payslip'].browse(data['payslips'])
        totals = self._get_total_totality(payslips)
        time_date = self._get_time_date(data['gen_date'])
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': payslips,
            'totals':totals,
            'date_time':time_date,
            'data': data,
        }

    def _get_total_totality(self, payslips):
        employees = 0
        basic = 0.00
        ot = 0.00
        additions = 0.00
        gross = 0.00
        other_ded = 0.00
        loans = 0.00
        nis = 0.00
        hsur = 0.00
        paye = 0.00
        total_ded = 0.00
        net = 0.00
        for payslip in payslips:
            employees += 1
            for line in payslip.line_ids:
                if line.code == "BASIC":
                    basic += line.amount
                elif line.code == "OT":
                    ot += line.amount
                elif line.code == "ADD":
                    additions += line.amount
                elif line.code == "GROSS":
                    gross += line.amount
                elif line.code == "O_DED":
                    other_ded += line.amount
                elif line.code == "LOAN":
                    loans += line.amount
                elif line.code == "NIS":
                    nis += line.amount
                elif line.code == "HSUR":
                    hsur += line.amount
                elif line.code == "PAYE":
                    paye += line.amount
                elif line.code == "NET":
                    net += line.amount
        total_ded = nis + hsur + paye

        basic = round(basic,2)
        ot = round(ot,2)
        additions = round(additions,2)
        gross = round(gross,2)
        other_ded = round(other_ded,2)
        loans = round(loans,2)
        nis = round(nis,2)
        hsur = round(hsur,2)
        paye = round(paye,2)
        total_ded = round(total_ded,2)
        net = round(net,2)

        return {
            "employees":employees,
            "basic":basic,
            "ot":ot,
            "additions":additions,
            "gross":gross,
            "other_ded":other_ded,
            "loans":loans,
            "nis":nis,
            "hsur":hsur,
            "paye":paye,
            "net":net,
            "total_deductions":total_ded,
        }
    
    def _get_time_date(self, date):
        spliter = date.split()
        date_str = spliter[0]
        time_str = spliter[1]
        return{
            "time":time_str,
            "date":date_str,
        }