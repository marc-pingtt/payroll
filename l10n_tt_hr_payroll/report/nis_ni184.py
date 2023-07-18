from odoo import models, _
from datetime import datetime
import calendar
from decimal import Decimal
import math


class NisReport(models.AbstractModel):
    _name = 'report.l10n_tt_hr_payroll.nis_ni184_template'

    def _get_report_values(self, docids, data):
        docs = self.env['hr.employee'].search([
            ('id', 'in', data['employee_ids'])])
        company = self.env.company

        bir_number = str(company.bir_file_number)
        new_bir_number = ['\u200B', '\u200B',
                          '\u200B', '\u200B', '\u200B', '\u200B']
        count_up = len(bir_number)
        count_down = len(new_bir_number)
        if (len(bir_number) <= 6 and company.bir_file_number != False):
            while count_up > 0:
                new_bir_number[count_down-1] = bir_number[count_up-1]
                count_up -= 1
                count_down -= 1
        bir_number = new_bir_number

        telephone_number = str(company.phone)
        new_telephone_number = ['\u200B', '\u200B',
                                '\u200B', '\u200B', '\u200B', '\u200B', '\u200B']
        count_down = len(telephone_number)
        count_up = len(new_telephone_number)
        if (company.phone != False):
            while count_up > 0:
                if (telephone_number[count_down - 1] != '-' and telephone_number[count_down - 1] != '(' and telephone_number[count_down - 1] != ')' and telephone_number[count_down - 1] != '+' and telephone_number[count_down - 1] != ' '):
                    new_telephone_number[count_up -
                                         1] = telephone_number[count_down - 1]
                    count_up -= 1
                count_down -= 1
        telephone_number = new_telephone_number

        nis_report_data = self.calculate_nis_report_data(data, docs)

        res = {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'data': data,
            'docs': docs,
            'company': company,
            'nis_report_data': nis_report_data,
            'created_by': self.env.user.display_name,
            'bir_number': bir_number,
            'telephone_number': telephone_number,

        }
        return res

    def calculate_nis_report_data(self, data, docs):
        number_of_forms = math.ceil(len(docs.ids)/11)
        values = []
        nib_numbers = [[] for _ in range(number_of_forms)]
        names = [[] for _ in range(number_of_forms)]
        dob = [[] for _ in range(number_of_forms)]
        date_employed_and_last_date_worked = [
            [] for _ in range(number_of_forms)]
        salary_for_period = [[] for _ in range(number_of_forms)]
        value_of_contributions = [[] for _ in range(number_of_forms)]
        total_value_per_employee = [[] for _ in range(number_of_forms)]
        total_value = [[] for _ in range(number_of_forms)]
        total_employees = [[] for _ in range(number_of_forms)]
        number_of_nis_periods = compute_number_mondays_inside_period(
            data.get('date_start'), data.get('date_end'))

        count = 0
        employee_counter = 0
        loop_total_value = 0

        for person in docs:
            employee_counter += 1

            nib_numbers[count].append(
                compute_nis_numbers(person.nis_number))
            names[count].append(person.display_name)

            dob[count].append(person.birthday)
            payslips = payslip_search(self, data.get(
                'date_start'), data.get('date_end'), person.contract_id.id)
            gross = 0
            for payslip in payslips:
                for line in payslip.line_ids:
                    if line.code == "GROSS":
                        gross += line.amount
            amount = compute_nis(
                payslip, gross, person.contract_id)
            value_of_contributions[count].append(round(amount/4, 2))
            loop_total_value += amount
            salary_for_period[count].append(gross)
            total_value_per_employee[count].append(amount)
            if (person.contract_id.date_end != False):
                date_employed_and_last_date_worked[count].append(
                    person.contract_id.date_end)
            else:
                date_employed_and_last_date_worked[count].append(
                    payslip.date_to)

            if (employee_counter == 11 or person.id == docs.ids[len(docs)-1]):
                total_value[count].append(loop_total_value)
                total_employees[count].append(employee_counter)
                loop_total_value = 0
                employee_counter = 0
                count += 1

        values.append({
            'nib_numbers': nib_numbers,
            'names': names,
            'dob': dob,
            'date_employed_and_last_date_worked': date_employed_and_last_date_worked,
            'salary_for_period': salary_for_period,
            'value_of_contributions': value_of_contributions,
            'total_value_per_employee': total_value_per_employee,
            'total_value': total_value,
            'total_employees': total_employees,
            'number_of_nis_periods': number_of_nis_periods,
            'number_of_forms': number_of_forms,

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


def payslip_search(self, report_period_start, report_period_end, contract):
    format_string = "%Y-%m-%d"
    report_period_start = datetime.strptime(
        report_period_start, format_string)
    report_period_end = datetime.strptime(
        report_period_end, format_string)

    domain = [('contract_id', '=', contract),
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


def compute_nis_numbers(nis_number):
    nis_blank_number = ['\u200B', '\u200B',
                        '\u200B', '\u200B', '\u200B', '\u200B', '\u200B', '\u200B']

    if (nis_number == False):
        return nis_blank_number

    nis_number = str(nis_number)
    new_nis_number = nis_blank_number
    count_up = len(nis_number)
    count_down = 8

    while (count_up > 0):
        new_nis_number[count_down - 1] = nis_number[count_up - 1]
        count_down -= 1
        count_up -= 1

    nis_number = new_nis_number
    return nis_number
