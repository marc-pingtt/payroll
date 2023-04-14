# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
import calendar
from decimal import Decimal
import math
from datetime import date


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        res.update({
            'compute_paye': compute_paye,
            'compute_health_surcharge': compute_health_surcharge,
            'compute_nis': compute_nis,
            'compute_additions': compute_additions,
        })
        return res

    def _get_localdict(self):
        res = super()._get_localdict()
        res['employee']['age'] = compute_age(res['employee']['birthday'])
        return res


def compute_age(birthday):
    today = date.today()
    return today.year - birthday.year - \
        ((today.month, today.day) < (birthday.month, birthday.day))


def compute_nis(employee, payslip, categories, contract):
    amount = 0.0
    contract = compute_active_contract(contract)
    total_mondays = compute_mondays_in_month(
        payslip.date_from.year, payslip.date_from.month)
    nis_rates = payslip.env['nis.rates'].search([])
    total_income = contract.wage + categories.ALW
    for line in nis_rates.nis_line_ids:
        monthly_earn = line.monthly_earnings.split()
        if monthly_earn[2] != "over":
            if Decimal(monthly_earn[0]) <= total_income <= Decimal(monthly_earn[2]):
                amount = line.employees_weekly_contri
                cal = Decimal(amount) * total_mondays
                return float(cal)
        else:
            amount = line.employees_weekly_contri
            cal = Decimal(amount) * total_mondays
            return float(cal)


def compute_active_contract(contracts):
    for contract in contracts:
        if contract.state == 'open':
            return contract

    print("Error No Open Contracts Available")
    return contracts  # This Only returns atm for troubleshooting purposes... but when fully deployed should not and instead kick an error message


def compute_projected_total_nis(employee, payslip, categories, contract):
    amount = 0.0
    month = payslip.date_from.month
    acculation_nis = 0.0

    if (month == 12):
        return float(acculation_nis)

    while (month < 12):
        month = month + 1
        total_mondays = compute_mondays_in_month(
            payslip.date_from.year, month)
        nis_rates = payslip.env['nis.rates'].search([])
        total_income = contract.wage + categories.ALW
        for line in nis_rates.nis_line_ids:
            monthly_earn = line.monthly_earnings.split()
            if monthly_earn[2] != "over":
                if Decimal(monthly_earn[0]) <= total_income <= Decimal(monthly_earn[2]):
                    amount = line.employees_weekly_contri
                    acculation_nis = Decimal(
                        amount) * total_mondays + Decimal(acculation_nis)
            else:
                amount = line.employees_weekly_contri
                acculation_nis = Decimal(
                    amount) * total_mondays + Decimal(acculation_nis)
    return float(acculation_nis)


def compute_mondays_in_month(year, month):
    return len([1 for i in calendar.monthcalendar(year, month) if i[0] != 0])


def compute_periods_remaining_nis(payslip):
    year = payslip.date_from.year
    month = payslip.date_from.month
    periods_remaining = compute_current_period(payslip)
    if (month != 12):
        while month < 12:
            month = month + 1
            periods_remaining = periods_remaining + \
                compute_mondays_in_month(year, month)
    return periods_remaining


def compute_health_surcharge(employee, payslip, categories):
    total_mondays = compute_mondays_in_month(
        payslip.date_from.year, payslip.date_from.month)
    basic_sal_week = (categories.BASIC * 12) / 52
    if basic_sal_week <= 109:
        health_surcharge = Decimal(
            payslip.rule_parameter('HSUR_LR')) * total_mondays
    else:
        health_surcharge = Decimal(
            payslip.rule_parameter('HSUR_UR')) * total_mondays
    return float(health_surcharge)


def compute_projected_health_surcharge(employee, payslip, categories):
    month = payslip.date_from.month
    accumulation_hsur = 0.0

    if (month == 12):
        return float(accumulation_hsur)
    while (month < 12):
        month = month + 1
        total_mondays = compute_mondays_in_month(
            payslip.date_from.year, month)
        basic_sal_week = (categories.BASIC * 12) / 52
        if basic_sal_week <= 109:
            health_surcharge = Decimal(
                payslip.rule_parameter('HSUR_LR')) * total_mondays
            accumulation_hsur = health_surcharge + Decimal(accumulation_hsur)
        else:
            health_surcharge = Decimal(
                payslip.rule_parameter('HSUR_UR')) * total_mondays
            accumulation_hsur = health_surcharge + Decimal(accumulation_hsur)
    return float(accumulation_hsur)


def relevant_by_amount(contract, payslip, parameter):
    amount = 0
    if (contract.date_start.year == payslip.date_from.year):
        amount = eval("contract." + parameter)
    return abs(amount)


def compute_paye(payslip, categories, contract, employee):
    contract = compute_active_contract(contract)
    periods_remaining = compute_periods_remaining_month(payslip)
    # TODO: This assignment uses abs but the function returns a result * -1. This is confusing.
    paye_year_to_date = abs(compute_paye_year_to_date(payslip, contract))
    # TODO: This assignment uses abs but the function returns a result * -1. This is confusing.
    nis_year_to_date = abs(compute_nis_year_to_date(payslip, contract))

    income_year_to_date = compute_income_year_to_date(payslip, contract)

    deductions_year_to_date = compute_deductions_year_to_date(payslip)

    projected_income = compute_projected_income(
        periods_remaining, categories)

    annual_income = compute_annual_income(
        income_year_to_date, projected_income, payslip)

    nis_tax_allowance = compute_nis_tax_allowance(
        categories.NIS, payslip, contract)

    annual_deductions = compute_annual_deductions(
        payslip, deductions_year_to_date, round(nis_tax_allowance, 2), annual_income, contract, nis_year_to_date)

    annual_tax_credits = compute_annual_tax_credits(payslip, contract)

    chargeable_income = compute_chargeable_income(
        annual_income, annual_deductions)

    annual_paye = compute_annual_paye(
        annual_income, chargeable_income, payslip, annual_tax_credits)
    annual_paye = round(annual_paye, 2)

    remaining_paye = compute_remaining_paye(annual_paye, paye_year_to_date)
    remaining_paye = round(remaining_paye, 2)

    categories.ALW = categories.ALW + compute_additions(payslip, contract)

    return float(compute_monthly_paye(remaining_paye, periods_remaining))


def compute_nis_tax_allowance(nis, payslip, contract):
    return (nis * payslip.rule_parameter('NIS_%'))


def compute_periods_remaining_month(payslip):
    end_month = 12
    start_month = payslip.date_from.month
    return end_month - start_month + 1


def _get_year_to_date_amount_for_rule(payslip, rule):
    return payslip.sum(rule, datetime(payslip.date_from.year, 1, 1), payslip.date_from)


def compute_paye_year_to_date(payslip, contract):
    paye_year_to_date = _get_year_to_date_amount_for_rule(payslip, 'PAYE')
    return paye_year_to_date + (relevant_by_amount(contract, payslip, "prior_paye_paid")*-1)


def compute_nis_year_to_date(payslip, contract):
    nis_year_to_date = _get_year_to_date_amount_for_rule(payslip, 'NIS')
    return (nis_year_to_date + (relevant_by_amount(contract, payslip, "prior_nis_paid") * -1))


def compute_hsur_year_to_date(payslip, contract):
    hsur_year_to_date = _get_year_to_date_amount_for_rule(payslip, 'HSUR')
    return hsur_year_to_date + (relevant_by_amount(contract, payslip, "prior_hsur_paid") * -1)


def compute_income_year_to_date(payslip, contract):
    income_year_to_date = _get_year_to_date_amount_for_rule(payslip, 'GROSS')
    return income_year_to_date + relevant_by_amount(contract, payslip, "prior_earnings")


def compute_deductions_year_to_date(payslip):
    deductions_year_to_date = _get_year_to_date_amount_for_rule(payslip, 'DED')
    return deductions_year_to_date


def allowance_year_to_date(payslip):
    allowances_year_to_date = _get_year_to_date_amount_for_rule(payslip, 'ADD')
    return allowances_year_to_date


def compute_projected_income(periods_remaining, categories):
    salary = categories.BASIC
    allowance = categories.ALW
    projected_income = (salary + allowance) * periods_remaining
    return projected_income


def compute_annual_income(income_year_to_date, projected_income, payslip):
    annual_income = income_year_to_date + \
        projected_income + allowance_year_to_date(payslip)
    return annual_income


def compute_projected_nis_deductions(payslip, nis_tax_allowance_month):
    remaining_periods_nis = compute_periods_remaining_nis(payslip)
    current_period = compute_current_period(payslip)
    weekly_nis = nis_tax_allowance_month/current_period
    return remaining_periods_nis * weekly_nis


def compute_current_period(payslip):
    year = payslip.date_from.year
    month = payslip.date_from.month
    current_period = compute_mondays_in_month(year, month)
    return current_period


def compute_valid_credits_or_deductions_for(payslip, contract, item_name, tax_field):
    amount = 0
    aggregator = eval("contract." + tax_field)
    items = [item for item in aggregator if is_valid_cred_and_deduct(
        item_name, payslip, aggregator)]

    for item in items:
        amount += item.amount

    return abs(amount)


def between_dates(date, date_from, date_to):
    return date_from <= date <= date_to


def after_date(date, date_from):
    return date_from < date


def between_dates(date, date_from, date_to):
    return date_from <= date <= date_to


def after_date(date, date_from):
    return date_from < date


def before_date(date, date_to):
    return date < date_to


def same_date(date, date_to):
    return date == date_to


def is_valid_cred_and_deduct(cred_duc_name, payslip, extras):

    for extra in extras:

        if (extra.year_valid_to != False):
            if (extra.type.name == cred_duc_name and (extra.year_valid_from < payslip.date_to or extra.year_valid_to >= payslip.date_to)):
                return True
            if (extra.type.name == cred_duc_name and extra.year_valid_from < payslip.date_to):
                return True

        if (extra.type.name == cred_duc_name and extra.year_valid_from.year >= payslip.date_from.year):
            if (payslip.date_from.month >= extra.year_valid_from.month):
                return True

        # Place Holder Function just to get National Tax Savings Bond working, will refactor to make nicer.
        NTSB = "NATIONAL TAX SAVINGS BONDS MATURITY YEAR "
        if (cred_duc_name == (NTSB + '5') or cred_duc_name == (NTSB + '7') or cred_duc_name == (NTSB + '10')):
            if (payslip.date_from.year == extra.year_valid_from.year + 5 or payslip.date_from.year == extra.year_valid_from.year + 7 or payslip.date_from.year == extra.year_valid_from.year + 10):
                return True

    return False


def compute_additions(payslip, contract):
    contract = compute_active_contract(contract)
    amount = 0

    def is_valid_addition(addition, payslip):

        if (addition.year_valid_to != False):
            if (addition.year_valid_from < payslip.date_to and addition.year_valid_to >= payslip.date_to):
                return True
            if (addition.year_valid_from < payslip.date_to and addition.year_valid_to >= payslip.date_to):
                return True

        if (addition.year_valid_from < payslip.date_to and addition.year_valid_to == False):
            return True

        if (addition.year_valid_from.month == payslip.date_from.month and addition.year_valid_from.year == payslip.date_from.year):
            return True

        return False

    additions = [addition for addition in contract.salary_additions if is_valid_addition(
        addition, payslip)]

    for addition in additions:
        amount += addition.amount

    return amount


def compute_greater_than_for(amount, limit):
    if (amount > limit):
        return limit
    return amount


def compute_greater_than_for_with_percentile_range(amount, payslip, rule_prefix):
    if (amount/100*payslip.rule_parameter(rule_prefix + '_%') > payslip.rule_parameter(rule_prefix + '_V')):
        return payslip.rule_parameter(rule_prefix + '_V')
    return amount


def compute_tertiary_deductions(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "TERTIARY EDUCATION EXPENSES", "tax_deductions")
    limit = payslip.rule_parameter('TEDEXP')
    return compute_greater_than_for(amount, limit)


def compute_first_time_home_owner(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "FIRST TIME HOME OWNER", "tax_deductions")
    limit = payslip.rule_parameter('FTHO')
    return compute_greater_than_for(amount, limit)


def compute_deed_of_covenant(payslip, contract, chargeable_income):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "DEED OF COVENANT", "tax_deductions")
    limit = chargeable_income/100*payslip.rule_parameter('DOCOV')
    return compute_greater_than_for(amount, limit)


def compute_contributions(payslip, contract, nis_projected_deductions):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "CONTRIBUTIONS/PREMIUMS PAID", "tax_deductions") + abs(nis_projected_deductions)
    limit = payslip.rule_parameter('CONTRIB')
    return compute_greater_than_for(amount, limit)


def compute_alimony_or_maintainance(payslip, contract):
    return compute_valid_credits_or_deductions_for(payslip, contract, "ALIMONY / MAINTAINANCE", "tax_deductions")


def compute_travelling_expenses(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "TRAVELLING EXPENSES", "tax_deductions")
    return amount/100*payslip.rule_parameter('TRAV_EXP')


def compute_solar_water_heater(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "SOLAR WATER HEATER", "tax_credits")
    return compute_greater_than_for_with_percentile_range(amount, payslip, "SWH")


def compute_cng_cylinders(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "CNG KIT AND CYLINDER", "tax_credits")
    return compute_greater_than_for_with_percentile_range(amount, payslip, "CNG")


def compute_guesthouse_conversion(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "GUEST HOUSE CONVERSION", "tax_deductions")
    return amount


def compute_venture_tax_credit(payslip, contract):
    amount = compute_valid_credits_or_deductions_for(
        payslip, contract, "VENTURE CAPITAL INVESTMENT", "tax_credits")
    if (amount != 0):
        return amount*payslip.rule_parameter("VCITC_%")
    return amount


def compute_national_tax_free_savings_bond(payslip, contract):
    amount = 0
    array_year = [payslip.rule_parameter('NTFSB_5'), payslip.rule_parameter(
        'NTFSB_7'), payslip.rule_parameter('NTFSB_10')]
    year = 0
    while year <= array_year[2]:
        if ([credit for credit in contract.tax_credits if credit.type.name == "NATIONAL TAX SAVINGS BONDS MATURITY YEAR " + str(year) and (credit.year_valid_from.year + payslip.rule_parameter('NTFSB_' + str(year))) == payslip.date_to.year]):
            amount += compute_valid_credits_or_deductions_for(
                payslip, contract, "NATIONAL TAX SAVINGS BONDS MATURITY YEAR " + str(year), "tax_credits")
        year += 1
    return compute_greater_than_for_with_percentile_range(amount, payslip, "NTFSB")


def compute_annual_tax_credits(payslip, contract):
    annual_credits = 0

    annual_credits += compute_venture_tax_credit(payslip, contract)

    annual_credits += compute_national_tax_free_savings_bond(payslip, contract)

    annual_credits += compute_solar_water_heater(payslip, contract)

    annual_credits += compute_cng_cylinders(payslip, contract)

    return round(annual_credits, 2)


def compute_annual_deductions(payslip, deductions_year_to_date, nis_tax_allowance, annual_income, contract, nis_year_to_date):
    annual_deductions = 0

    if (nis_year_to_date != 0):
        nis_deductable_year_to_date = compute_nis_tax_allowance(
            nis_year_to_date, payslip, contract)
        annual_deductions = nis_deductable_year_to_date + annual_deductions

    nis_projected_deductions = round(
        compute_projected_nis_deductions(payslip, nis_tax_allowance), 2)

    annual_deductions += deductions_year_to_date + \
        payslip.rule_parameter('PALLOW')

    annual_deductions += compute_tertiary_deductions(payslip, contract)

    annual_deductions += compute_first_time_home_owner(payslip, contract)

    annual_deductions += compute_deed_of_covenant(
        payslip, contract, annual_income)

    annual_deductions += compute_contributions(
        payslip, contract, nis_projected_deductions)

    annual_deductions += compute_alimony_or_maintainance(payslip, contract)

    annual_deductions += compute_travelling_expenses(payslip, contract)

    annual_deductions += compute_guesthouse_conversion(payslip, contract)

    annual_deductions = round(annual_deductions, 2)

    return annual_deductions


def compute_chargeable_income(annual_income, annual_deductions):
    chargeable_income = annual_income - annual_deductions
    return chargeable_income


def compute_annual_paye(annual_income, chargeable_income, payslip, annual_tax_credits):
    rate = Decimal(payslip.rule_parameter('PAYE_LB'))
    if annual_income > Decimal(payslip.rule_parameter('PAYE_T')):
        rate = Decimal(payslip.rule_parameter('PAYE_UB'))

    annual_paye = (Decimal(chargeable_income) * rate) - \
        Decimal(annual_tax_credits)

    if (annual_paye < 0):
        annual_paye = 0

    return annual_paye


def compute_remaining_paye(annual_paye, paye_year_to_date):
    remaining_paye = Decimal(annual_paye) - Decimal(paye_year_to_date)
    return remaining_paye


def compute_monthly_paye(remaining_paye, periods_remaining):
    paye = round(remaining_paye / periods_remaining, 2)
    return paye
