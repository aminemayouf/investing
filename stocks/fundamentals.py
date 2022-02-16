import argparse
import numpy as np
from tabulate import tabulate
import config
from utils.millify import millify
from utils.translate import Translator
import scrappers.investing as inv
from pickers.buffet import Buffet
from pickers.mayer import Mayer
from pickers.slater import Slater

parser = argparse.ArgumentParser(description="Perform a fundamental analysis of a compagny")
parser.add_argument("ISIN", type=str, help="The company's ISIN")
parser.add_argument("-l", "--language", default="en", help="Language")

args = parser.parse_args()

# get translator
config.language = args.language
tr = Translator(args.language)

# convert the company's ISIN to uppercase
ISIN = args.ISIN.upper()
equity = inv.Equity(ISIN)

def __safe_get(value, index):
    return None if value is None else value[index]

### exctract data
market_cap = equity.market_cap()
# income statement
income_statement = equity.income_statement

annual_revenue = income_statement.total_revenue()
revenue = __safe_get(annual_revenue, 0)
ebit = __safe_get(income_statement.net_income_before_taxes(), 0)
earnings = __safe_get(income_statement.net_income_after_taxes(), 0)
net_income_applicable_to_common_shares = __safe_get(income_statement.income_available_to_common_excluding_extraordinary_items(), 0)
gross_profit = __safe_get(income_statement.gross_profit(), 0)
operating_income = __safe_get(income_statement.operating_income(), 0)
net_income = __safe_get(income_statement.net_income(), 0)
interest_income = __safe_get(income_statement.interest_income(), 0)
provision_for_income_taxes = __safe_get(income_statement.provision_for_income_taxes(), 0)
depreciation_amortization = __safe_get(income_statement.depreciation_amortization(), 0)

ebitda = None
if net_income and interest_income and provision_for_income_taxes and depreciation_amortization:
    ebitda = net_income + interest_income + provision_for_income_taxes + depreciation_amortization

# balance sheet
balance_sheet = equity.balance_sheet

common_shares_outstaning = __safe_get(balance_sheet.total_common_shares_outstanding(), 0)
total_assets = __safe_get(balance_sheet.total_assets(), 0)
stockholder_equity = __safe_get(balance_sheet.total_equity(), 0)
current_assets = __safe_get(balance_sheet.total_current_assets(), 0)
current_liabilities = __safe_get(balance_sheet.total_current_liabilities(), 0)
long_term_debt = __safe_get(balance_sheet.total_long_term_debt(), 0)
cash_and_cash_equivalents = __safe_get(balance_sheet.cash_and_equivalents(), 0)
other_short_term_investments = __safe_get(balance_sheet.short_term_investments(), 0)
accounts_receivable = __safe_get(balance_sheet.accounts_receivable(), 0)
short_term_debt = __safe_get(balance_sheet.short_term_debt(), 0)

# ratios
ratios = equity.ratios

##########################################################################################################################

print("\n" + tr("Fundamental analysis of") + " {} :\n".format(equity.name))

# predict next year earnings using linear regression
l = len(annual_revenue)
if l >= 3:
    n = int(np.floor(np.divide(l, 3)))
    m = l - (n * 2)

    y1 = 0
    e1 = 0
    for i in reversed(range(0, n)):
        y1 += int(income_statement.column(i)[-4:])
        e1 += annual_revenue[i]
    y1 /= n
    e1 /= n
    m1 = (y1, e1)

    y2 = 0
    e2 = 0
    for i in reversed(range(n, l - n)):
        y2 += int(income_statement.column(i)[-4:])
        e2 += annual_revenue[i]
    y2 /= l - (n * 2)
    e2 /= l - (n * 2)
    m2 = (y2, e2)

    y3 = 0
    e3 = 0

    for i in reversed(range(l-n, l)):
        y3 += int(income_statement.column(i)[-4:])
        e3 += annual_revenue[i]
    y3 /= n
    e3 /= n
    m3 = (y3, e3)

    p = ((m1[0]+m2[0]+m3[0]) / 3, (m1[1]+m2[1]+m3[1]) / 3)

    a = (m3[1]-m1[1])/(m3[0]-m1[0])
    b = p[1] - (a * p[0])

    earnings_table_headers = []
    earnings_table = []
    for i in reversed(range(l)):
            earnings_table_headers.append(income_statement.column(i)[-4:])
            earnings_table.append(annual_revenue[i])

    earnings_table_headers.append("Est. {}".format(int(income_statement.column(i)[-4:]) + 1))
    earnings_table.append(millify(a * (int(income_statement.column(i)[-4:]) + 1) + b))
    print("\n* " + tr("Change in net income") + ":\n\n+" + tabulate([earnings_table], headers=earnings_table_headers) + "\n")

## profitability
print(tr("Profitability") + ":")

# gross margin
if gross_profit and revenue:
    gross_margin = gross_profit / revenue * 100
    print(tr("Gross margin") + " (TTM): {:.2f}%".format(gross_margin))

# operating margin
if operating_income and revenue:
    operating_margin = operating_income / revenue * 100
    print(tr("Operating margin") + " (TTM): {:.2f}%".format(operating_margin))

# net margin
if net_income and revenue:
    net_margin = net_income / revenue * 100
    print(tr("Net margin") + " (TTM): {:.2f}%".format(net_margin))

## overall financial performance
print("\n" + tr("Overral financial performance") + ":")

if short_term_debt and long_term_debt and market_cap and cash_and_cash_equivalents:
    total_debt =  short_term_debt + long_term_debt
    enterprise_value = market_cap + total_debt - cash_and_cash_equivalents
    # ev / ebitda ratio
    if ebitda:
        ev_ebitda_ratio = enterprise_value / ebitda
        comment = tr("bad")
        if ev_ebitda_ratio < 11:
            comment = tr("excellent")
        elif ev_ebitda_ratio < 14:
            comment = tr("good")
        print("EV/EBITDA: {:.2f} -> {}".format(enterprise_value / ebitda, comment))

    # ebit / ev multiple
    if ebit:
        ebit_ev_multiple = ebit / enterprise_value
        print("EBIT/EV: {:.2f}x".format(ebit_ev_multiple))

# eps
if common_shares_outstaning:
    if net_income_applicable_to_common_shares:
        basic_eps = net_income_applicable_to_common_shares / common_shares_outstaning
    elif net_income:
        basic_eps = net_income / common_shares_outstaning

    if basic_eps and market_cap:
        # pe ratio
        per = (market_cap / common_shares_outstaning) / basic_eps
        comment = tr("bad")
        if per <= 10:
            comment = tr("excellent")
        elif per <= 12:
            comment = tr("good")
        print("P/E Ratio: {:.2f} -> {}".format(per, comment))


## management effectivness
print("\n" + tr("Management effectivness") + ":")

# roa (return on assets)
if net_income and total_assets:
    roa = net_income / total_assets * 100
    comment = tr("bad")
    if roa > 5:
        comment = tr("good")
    if roa > 10:
        comment = tr("excellent")
    print("ROA (TTM): {:.2f}% -> {}".format(roa, comment))

# roce (return on capital employed)
if total_assets and current_liabilities and ebit:
    capital_employed = total_assets - current_liabilities
    roce = ebit / capital_employed * 100
    comment = "..."
    if roce > 20:
        comment = tr("excellent")
    print("ROCE (TTM): {:.2f}% -> {}".format(roce, comment))

# roe (return on equity)
if net_income and stockholder_equity:
    roe = net_income / stockholder_equity * 100
    comment = tr("bad")
    if roe >= 15 and roe <= 20:
        comment = tr("good")
    elif roe > 20:
        comment = tr("excellent")
    print("ROE (TTM): {:.2f}% -> {}".format(roe, comment))

## balance sheet
print("\n" + tr("Balance sheet") + ":")

# current ratio
if current_liabilities and current_liabilities:
    current_ratio = current_assets / current_liabilities
    if not current_ratio:
        current_ratio = current_assets / current_liabilities
    if current_ratio > 1.5:
        comment = tr("good")
    else:
        comment = tr("bad")
        if current_ratio < 1:
            comment = tr("very bad")
    print(tr("Current ratio") + " (TTM): {:.2f} -> {}".format(current_ratio, comment))

# quick ratio
if cash_and_cash_equivalents and other_short_term_investments and accounts_receivable and current_liabilities:
    quick_ratio = (cash_and_cash_equivalents + other_short_term_investments + accounts_receivable) / current_liabilities
    if quick_ratio > 1:
        if quick_ratio <= 1.5:
            comment = tr("good")
        elif quick_ratio > 1.5:
            comment = tr("excellent")
    else: 
        comment = tr("bad")
    print("QR (TTM): {:.2f} -> {}".format(quick_ratio, comment))

buffet = Buffet(equity)
buffet.evaluation()

mayer = Mayer(equity)
mayer.evaluation()

slater = Slater(equity)
slater.evaluation()
