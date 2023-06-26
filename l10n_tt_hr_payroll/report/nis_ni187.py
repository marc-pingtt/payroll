from odoo import models
from datetime import datetime
import calendar
from decimal import Decimal


class NisReportDues(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.nis_ni187_template'

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
            'nis_report_data': self.nis_report_data(data, docs),
        }
        return res

    def nis_report_data(self, data, docs):
        values = []
        main_lines = []
        lines = []
        contributions = 0
        penality = 0
        intrest = 0
        total_due = 0
        total_employees = 0
        payslips = payslip_search(self, data.get(
            'date_start'), data.get('date_end'))
        gross = 0
        for person in docs:
            total_employees += 1
            for payslip in payslips:
                for line in payslip.line_ids:
                    if line.code == "GROSS":
                        gross += line.amount
                    if line.code == "NIS":
                        contributions += Decimal(line.amount)
                    total_due += Decimal(compute_nis(payslip,
                                                     gross, payslip.contract_id))
        balance = total_due - contributions
        amount_paid = contributions

        values.append({
            'main_lines': main_lines,
            'lines': lines,
            'contributions': contributions,
            'penality': penality,
            'intrest': intrest,
            'total_due': total_due,
            'balance': balance,
            'amount_paid': amount_paid,
            'total_employees': total_employees,

        })
        return values


def compute_mondays_in_month(year, month):
    return len([1 for i in calendar.monthcalendar(year, month) if i[0] != 0])


def compute_number_mondays_inside_month(date_start, date_end):
    mondays_gone = 0
    day_counter = date_start.day

    format_string = "%Y-%m-%d"

    while (day_counter <= date_end.day):
        date_string = str(date_end.year)+"-" + \
            str(date_end.month)+"-"+str(day_counter)
        datetime_obj = datetime.strptime(date_string, format_string)

        if datetime_obj.weekday() == 0:
            mondays_gone += 1

        day_counter += 1

    return mondays_gone


def compute_number_mondays_inside_period(date_from, date_to):
    monday_counter = 0

    format_string = "%Y-%m-%d"
    date_from = datetime.strptime(
        date_from, format_string)
    date_to = datetime.strptime(
        date_to, format_string)

    from_month = date_from.month

    year_counter = date_from.year + 1

    if (date_from.year == date_to.year and date_from.month != date_to.month):
        while (from_month < date_to.month):
            monday_counter += compute_mondays_in_month(
                date_from.year, from_month)
            from_month += 1

    if (date_from.year == date_to.year and (date_from.month == date_to.month or from_month == date_to.month)):
        monday_counter += compute_number_mondays_inside_month(
            date_from, date_to)

    if (date_from.year != date_to.year):

        date_string_this_year = str(
            date_from.year)+"-"+str(date_from.max.month)+"-"+str(date_from.max.day)
        datetime_obj_this_year = datetime.strptime(
            date_string_this_year, format_string)

        monday_counter += compute_number_mondays_inside_period(
            date_from, datetime_obj_this_year)

        date_string_next_year = str(
            year_counter)+"-"+str(date_from.min.month)+"-"+str(date_from.min.day)
        datetime_obj_next_year = datetime.strptime(
            date_string_next_year, format_string)

        monday_counter += compute_number_mondays_inside_period(
            datetime_obj_next_year, date_to)

    return monday_counter


def payslip_search(self, report_period_start, report_period_end):
    format_string = "%Y-%m-%d"
    report_period_start = datetime.strptime(
        report_period_start, format_string)
    report_period_end = datetime.strptime(
        report_period_end, format_string)

    domain = [
        ('date_from', '>=', report_period_start),
        ('date_to', '<=', report_period_end)]
    payslips = self.env['hr.payslip'].search(domain).sudo()
    return payslips


def compute_nis(payslip, total_income, contract):
    amount = 0.0
    total_mondays = compute_mondays_in_month(
        payslip.date_from.year, payslip.date_from.month)
    nis_rates = payslip.env['nis.rates'].search([])
    for line in nis_rates.nis_line_ids:
        monthly_earn = line.monthly_earnings.split()
        if monthly_earn[2] != "over":
            if Decimal(monthly_earn[0]) <= total_income <= Decimal(monthly_earn[2]):
                amount = line.employees_weekly_contri
                if (contract.is_pension == True):
                    amount = 0
                cal = Decimal(amount) * total_mondays
                return Decimal(cal)
        else:
            amount = line.employees_weekly_contri
            if (contract.is_pension == True or contract.wage <= 199):
                amount = 0
            cal = Decimal(amount) * total_mondays
            return Decimal(cal)
