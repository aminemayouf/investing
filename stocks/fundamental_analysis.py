import argparse
import json
import os
import urllib.request
import requests
import numpy as np
import gettext
from tabulate import tabulate
from utils.millify import millify


def printv(msg):
    if args.verbose:
        print(msg)


parser = argparse.ArgumentParser(description='Perform a fundamental analysis of a compagny')
parser.add_argument('symbol', type=str, help='The company symbol')
parser.add_argument('-k', '--apikey', type=str, help='API key')
parser.add_argument('-u', '--update', action='store_true', default=False,
                    help='Update cached company data')
parser.add_argument('-l', '--locale', default='en',
                    help='Language')                    
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Show additional traces')

args = parser.parse_args()

_ = gettext.gettext
if not args.locale == 'en':    
    if args.locale == 'fr':
        fr = gettext.translation('fr_FR', localedir='locales', languages=['fr'])
        fr.install()
        _ = fr.gettext
    else:
        print(_('The specified language was not found, the default language will be used'))

# fetch api key(s)
apikeys = []
if args.apikey:
    apikeys.append(args.apikey)
else:
    keys_dir = './keys'
    if not os.path.exists(keys_dir):
        printv('Creating keys directory')
        os.mkdir(keys_dir)
        print(_('No keys found, please provide an API key or create an empty file and name it with the API key and place you key in key(s) under <keys> directory'))
        exit(0)
    for file in os.listdir(keys_dir):
        apikeys.append(file)
update = args.update

# convert company symbol to uppercase
symbol = args.symbol.upper()

# create cache directory if it doesn't exit
cache_dir = './cache'
if not os.path.exists(cache_dir):
    printv('Creating cache folder')
    os.mkdir(cache_dir)

filename = os.path.join(cache_dir, symbol + '.json')
if not os.path.exists(filename):
    update = True

data = []
if update:
    # fetch company's data
    print(_('Downloading the company\'s data...'))
    # fetch company's financials
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-financials"
    querystring = {"symbol": symbol}
    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': apikeys[0]
    }
    response = requests.request("GET", url, headers=headers, params=querystring,)
    data.append(response.json())
    # fetch company's balance-sheet
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-balance-sheet"
    response = requests.request("GET", url, headers=headers, params=querystring,)
    if not response:
        print(_('The company\'s data could not be downloaded for the following reason') +': ', response.reason)
    else:
        data.append(response.json())
        # store company data as json
        outfile = open(filename, 'w')
        json.dump(data, outfile, indent=4)
        print(_('Successfuly downloaded the company\'s data'))
else:
    print(_('Loading cached company\'s data...'))
    infile = open(filename)
    data = json.load(infile)
    print(_('Successfuly loaded cached company\'s data'))

print('\n')

## exctract infos
financials = data[0]
company_name = financials['quoteType']['longName']
market_cap = financials['summaryDetail']['marketCap']['raw']

if len(financials['earnings']) > 0:
    earnings = financials['earnings']['financialsChart']['yearly']
else:
    earnings = None
    printv('WARNING: Financials value could not be found')

if earnings != None:    
    revenue = earnings[-1]['revenue']['raw']
else:
    revenue = None
    printv('WARNING: Revenue value could not be found')

ebit = financials['incomeStatementHistory']['incomeStatementHistory'][0]['ebit']['raw']

trailing_gross_profit = financials['timeSeries']['trailingGrossProfit'][0]['reportedValue']['raw']
trailing_operating_income = financials['timeSeries']['trailingOperatingIncome'][0]['reportedValue']['raw']

if len(financials['timeSeries']['trailingInterestExpense']) > 0:
    interest_expense = financials['timeSeries']['trailingInterestExpense'][0]['reportedValue']['raw']
elif len(financials['timeSeries']['annualInterestExpense']) > 0:
    interest_expense = financials['timeSeries']['annualInterestExpense'][-1]['reportedValue']['raw']
else:
    interest_expense = None
    printv('WARNING: Interest expenses value could not be found')

if len(financials['timeSeries']['trailingNetIncome']) > 0:
    net_income = financials['timeSeries']['trailingNetIncome'][0]['reportedValue']['raw']
elif len(financials['timeSeries']['annualNetIncome']) > 0:
    net_income = financials['timeSeries']['annualNetIncome'][-1]['reportedValue']['raw']
else:
    net_income = None
    printv('WARNING: Net income value could not be found')

if len(financials['timeSeries']['trailingSellingGeneralAndAdministration']) > 0:
    sga = financials['timeSeries']['trailingSellingGeneralAndAdministration'][0]['reportedValue']['raw']
elif len(financials['timeSeries']['annualSellingGeneralAndAdministration']) > 0:
    sga = financials['timeSeries']['annualSellingGeneralAndAdministration'][-1]['reportedValue']['raw']
else:
    sga = None
    printv('WARNING: Selling General & Administration value could not be found')

trailing_operating_expense = financials['timeSeries']['trailingOperatingExpense'][0]['reportedValue']['raw']

balance_sheet = data[1]
# common_shares = balance_sheet['balanceSheetHistory']['balanceSheetStatements'][0]['commonStock']['raw']
# net_income_applicable_to_common_shares = financials['incomeStatementHistory']['incomeStatementHistory'][0]['netIncomeApplicableToCommonShares']['raw']
total_assets = balance_sheet['balanceSheetHistory']['balanceSheetStatements'][0]['totalAssets']['raw']
stockholder_equity =  balance_sheet['balanceSheetHistory']['balanceSheetStatements'][0]['totalStockholderEquity']['raw']
property_plant_equipment = balance_sheet['balanceSheetHistory']['balanceSheetStatements'][0]['propertyPlantEquipment']['raw']
# intangible_assets = balance_sheet['balanceSheetHistory']['balanceSheetStatements'][0]['intangibleAssets']['raw']
current_assets = balance_sheet['timeSeries']['annualCurrentAssets'][-1]['reportedValue']['raw']
current_liabilities = balance_sheet['timeSeries']['annualCurrentLiabilities'][-1]['reportedValue']['raw']
long_term_debt = balance_sheet['timeSeries']['annualLongTermDebt'][-1]['reportedValue']['raw']
annual_cash_and_cash_equivalents = balance_sheet['timeSeries']['annualCashAndCashEquivalents']
cash_and_cash_equivalents = annual_cash_and_cash_equivalents[-1]['reportedValue']['raw']

annual_other_short_term_investments = balance_sheet['timeSeries']['annualOtherShortTermInvestments']
if len(annual_other_short_term_investments) > 0:
    other_short_term_investments = balance_sheet['timeSeries']['annualOtherShortTermInvestments'][-1]['reportedValue']['raw']
else:
    other_short_term_investments = 0
    printv('WARNING: Other short term investments value could not be found')

accounts_receivable = balance_sheet['timeSeries']['annualAccountsReceivable'][-1]['reportedValue']['raw']

# goodwill = balance_sheet['timeSeries']['annualGoodwill'][-1]['reportedValue']['raw']
# short_term_debt = balance_sheet['timeSeries']['annualCurrentDebt'][-1]['reportedValue']['raw']

cash_flow = financials['cashflowStatementHistory']['cashflowStatements']

capital_expenditures = None
if 'capitalExpenditures' in cash_flow[0]:
    capital_expenditures = cash_flow[0]['capitalExpenditures']['raw']
elif 'capitalExpenditures' in cash_flow[1]:
    apital_expenditures = cash_flow[1]['capitalExpenditures']['raw']

depreciation = None
if 'depreciation' in cash_flow[0]:
    depreciation = cash_flow[0]['depreciation']['raw']
elif 'depreciation' in cash_flow[1]:
    depreciation = cash_flow[1]['depreciation']['raw']

buffet_approved = 0
buffet_criterias = 0
buffet_approved_summary = ''
buffet_not_approved_summary = ''

slater_approved = 0
slater_criterias = 0
slater_approved_summary = ''
slater_not_approved_summary = ''

print('\n' + _('Fundamental analysis of') + ' {} :\n'.format(company_name))

# predict next year earnings using linear regression
n = int(np.floor(np.divide(len(earnings), 3)))
m = len(earnings) - (n * 2)

y1 = 0
e1 = 0
for i in range(0, n):
    y1 += earnings[i]['date']
    e1 += earnings[i]['earnings']['raw']
y1 /= n
e1 /= n
m1 = (y1, e1)

y2 = 0
e2 = 0
for i in range(n, len(earnings) - n):
    y2 += earnings[i]['date']
    e2 += earnings[i]['earnings']['raw']
y2 /= len(earnings) - (n * 2)
e2 /= len(earnings) - (n * 2)
m2 = (y2, e2)

y3 = 0
e3 = 0
for i in range(len(earnings)-n, len(earnings)):
    y3 += earnings[i]['date']
    e3 += earnings[i]['earnings']['raw']
y3 /= n
e3 /= n
m3 = (y3, e3)

p = ((m1[0]+m2[0]+m3[0]) / 3, (m1[1]+m2[1]+m3[1]) / 3)

a = (m3[1]-m1[1])/(m3[0]-m1[0])
b = p[1] - (a * p[0])

earnings_table_headers = []
earnings_table = []
for i in range(len(earnings)):
        earnings_table_headers.append(earnings[i]['date'])
        earnings_table.append(earnings[i]['earnings']['fmt'])

earnings_table_headers.append('Est. {}'.format(earnings[-1]['date'] + 1))
earnings_table.append(millify(a * (earnings[-1]['date'] + 1) + b))
printv('\n* ' + _('Change in net income') + ':\n\n+' + tabulate([earnings_table], headers=earnings_table_headers) + '\n')

# market cap
slater_criterias += 1
if market_cap < 5e6:
    slater_approved += 1
    slater_approved_summary += '\n-' + _('Slater likes smallcaps')
else:
    slater_not_approved_summary += '\n-' + _('Slater prefers smallcaps')

## profitability
printv(_('Profitability') + ':')

# gross margin
gross_margin = trailing_gross_profit / revenue * 100
buffet_criterias += 1
if gross_margin > 40:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + _('The gross margin is higher than') + ' 40% ({:.2f}%)'.format(gross_margin)
else:
    buffet_not_approved_summary += '\n-' + _('The gross margin is lower than') + ' 40% ({:.2f}%)'.format(gross_margin)
printv(_('Gross margin') + ' (TTM): {:.2f}%'.format(gross_margin))

# operating margin
operating_margin = trailing_operating_income / revenue * 100
printv(_('Operating margin') + ' (TTM): {:.2f}%'.format(operating_margin))

# net margin
net_margin = net_income / revenue * 100
buffet_criterias += 1
if net_margin > 20:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + _('The net margin is higher than') + ' 20% ({:.2f}%)'.format(net_margin)
else:
    buffet_not_approved_summary += '\n-' + _('The net margin is lower than') + ' 20% ({:.2f}%)'.format(net_margin)
printv(_('Net margin') + ' (TTM): {:.2f}%'.format(net_margin))

# # eps
# basic_eps = net_income_applicable_to_common_shares / common_shares
# printv('EPS: {}'.format(basic_eps))

## management effectivness
printv('\n' + _('Management effectivness') + ':')
# roa
roa = net_income / total_assets * 100
comment = _('bad')
if roa > 5:
    comment = _('good')
if roa > 10:
    comment = _('excellent')
printv('ROA (TTM): {:.2f}% -> {}'.format(roa, comment))

# roce (return on capital employed)
slater_criterias += 1
capital_employed = total_assets - current_liabilities
roce = ebit / capital_employed * 100
comment = '-'
if roce > 20:
    comment = _('excellent')
    slater_approved += 1
    slater_approved_summary += '\n-' + _('The return on capital employed is higher than') + ' 20% ({:.2f}%)'.format(roce)
else:
    slater_not_approved_summary += '\n-' + _('The return on capital employed is lower than') + ' 20% ({:.2f}%)'.format(roce)
printv('ROCE (TTM): {:.2f}% -> {}'.format(roce, comment))

# roe
roe = net_income / stockholder_equity * 100
comment = _('bad')
if roe >= 15 and roe <= 20:
    comment = _('good')
elif roe > 20:
    comment = _('excellent')
printv('ROE (TTM): {:.2f}% -> {}'.format(roe, comment))

## balance sheet
printv('\n' + _('Balance sheet') + ':')

# current ratio
buffet_criterias += 1
current_ratio = current_assets / current_liabilities
if current_ratio > 1.5:
    comment = _('good')
    buffet_approved += 1
    buffet_approved_summary += '\n-' + _('The current ratio is higher than') + ' 1.5 ({:.2f})'.format(current_ratio)
    if (current_ratio > 2.5):
        buffet_approved_summary += '\n-' + _('However, you should note that the current ratio is higher than') + ' 2.5, ' + _('which may indicate mismanagement of money due to an inability to collect payments')
else:
    comment = _('bad')
    buffet_not_approved_summary += '\n-' + _('The current ratio is lower than') + ' 1.5 ({:.2f})'.format(current_ratio)
    if current_ratio < 1:
        comment = _('very bad')
        buffet_not_approved_summary += '\n-' + _('The company must acquire new debt to pay its debt obligations')
printv(_('Current ratio') + ' (TTM): {:.2f} -> {}'.format(current_ratio, comment))

# quick ratio
if other_short_term_investments != None:
    slater_criterias += 1
    quick_ratio = (cash_and_cash_equivalents + other_short_term_investments + accounts_receivable) / current_liabilities
    if quick_ratio > 1:
        slater_approved += 1
        slater_approved_summary += '\n-' + _('The company has good financials, it\'s QR is higher than') + ' 1 ({:.2f})'.format(quick_ratio)
        if quick_ratio <= 1.5:
            comment = _('good')
        elif quick_ratio > 1.5:
            comment = _('excellent')
    else: 
        comment = _('bad')
        slater_not_approved_summary += '\n-' + _('The company doesn\'t have good financials, it\'s QR is lower than') + ' 1 ({:.2f})'.format(quick_ratio)
    printv('QR (TTM): {:.2f} -> {}'.format(quick_ratio, comment))

if sga != None:
    buffet_criterias += 1
    sga_to_gross_margin_ratio = sga * 100 / trailing_gross_profit
    if sga_to_gross_margin_ratio < 30:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('Selling, General and Administrative expenses represent less than 30% of the gross margin') + ' ({:.2f}%)'.format(sga_to_gross_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('Selling, General and Administrative expenses represent more than 30% of the gross margin') + ' ({:.2f}%)'.format(sga_to_gross_margin_ratio)
# else:
#     operating_expense_to_gross_margin_ratio = trailing_operating_expense * 100 / trailing_gross_profit
#     if operating_expense_to_gross_margin_ratio < 70:
#         buffet_approved += 1
#         buffet_approved_summary += '\n-Les frais d\'exploitation représentent moins de 70% de la marge brute ({:.2f}%)'.format(operating_expense_to_gross_margin_ratio)
#     else:
#         buffet_not_approved_summary += '\n-Les frais d\'exploitation représentent plus de 70% de la marge brute ({:.2f}%)'.format(operating_expense_to_gross_margin_ratio)

# depretiation to gross margin
if depreciation != None:
    buffet_criterias += 1
    depreciation_to_gross_margin_ratio = depreciation * 100 / trailing_gross_profit
    if depreciation_to_gross_margin_ratio < 15:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('The depreciation is low') + ' ({:.2f}%)'.format(depreciation_to_gross_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('The depreciation is high') + ' ({:.2f}%)'.format(depreciation_to_gross_margin_ratio)

# interest expense to operating margin
if interest_expense != None:
    buffet_criterias += 1
    interest_expense_to_operating_margin_ratio = interest_expense * 100 / trailing_operating_income
    if interest_expense_to_operating_margin_ratio < 15:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('The interest expense is lower than') + ' 15% ({:.2f}%)'.format(interest_expense_to_operating_margin_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('The interest expense is higher than') + ' 15% ({:.2f}%)'.format(interest_expense_to_operating_margin_ratio)
    
# earnings trend
if earnings != None:
    buffet_criterias += 1
    slater_criterias += 1
    earnings_growth = 0
    consistent_growth = True
    for i in range(len(earnings)-1):
        sign = +1
        if earnings[i]['earnings']['raw'] > earnings[i+1]['earnings']['raw']:
            sign = -1
        earnings_growth += sign * (1 - (earnings[i]['earnings']['raw'] / earnings[i+1]['earnings']['raw'])) * 100
        if earnings_growth < 15:
            consistent_growth = False
    earnings_growth /= len(earnings)
    if earnings_growth > 0:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('The net earnings follow an upward trend over a period of') + (' {} ' + _('years') + ' ({:.2f}%)').format(len(earnings), earnings_growth)
    else:
        buffet_not_approved_summary += '\n-' + _('The net earnings follow a downward trend over a period of') + (' {} ' + _('years') + ' ({:.2f}%)').format(len(earnings), earnings_growth)
    if earnings_growth > 15:
        slater_approved += 1
        slater_approved_summary += '\n-' + _('The annual earnings growth rate is higher than') + ' 15% ({:.2f}%)'.format(earnings_growth)
    else:
        slater_not_approved_summary += '\n-' + _('The annual earnings growth rate is lower than') + ' 15% ({:.2f}%)'.format(earnings_growth)
    
# cash and cash equivalents
buffet_criterias += 1
cash_growth = 0
for i in range(len(annual_cash_and_cash_equivalents)-1):
    cash_growth += (1 - (annual_cash_and_cash_equivalents[i]['reportedValue']['raw'] / annual_cash_and_cash_equivalents[i+1]['reportedValue']['raw'])) * 100
    cash_growth /= len(annual_cash_and_cash_equivalents)
if cash_growth > 0:
    buffet_approved += 1
    # todo: check if it's generated by free cash flow
    buffet_approved_summary += '\n-' + _('The company has a significant amount of cash which increases by') + ' {:.2f}% '.format(cash_growth) + _('on average per year')
else:
    buffet_not_approved_summary += '\n-' + _('The company draws on it\'s cash')

# little to no debt
buffet_criterias += 1
long_term_debt_to_net_income_ratio = long_term_debt / net_income
if long_term_debt_to_net_income_ratio < 4:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + _('The company is in a strong position, its long-term debt to net income ratio is less than') + ' 4 ({:.2f})'.format(long_term_debt_to_net_income_ratio)
else:
    buffet_not_approved_summary += '\n-' + _('The company is not in a strong position, its long-term debt to net income ratio is greater than') + ' 4 ({:.2f})'.format(long_term_debt_to_net_income_ratio)

# inventory trend
inventory = balance_sheet['timeSeries']['annualInventory']
if len(inventory) > 0 and earnings != None:
    buffet_criterias += 1
    inline_with_each_other = True
    for i in range(len(inventory)-1):
        earnings_growth = (1 - (earnings[i]['earnings']['raw'] / earnings[i+1]['earnings']['raw'])) * 100
        inventory_growth = (1 - (inventory[i]['reportedValue']['raw'] / inventory[i+1]['reportedValue']['raw'])) * 100
        if np.sign(earnings_growth) != np.sign(inventory_growth):
            inline_with_each_other = False
            break
    if inline_with_each_other:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('Inventories move in line with profits')
    else:
        buffet_not_approved_summary += '\n-' + _('Inventories do not move in line with profits (to be taken into account only if the products sold may become obsolete)')

# ppe
buffet_criterias += 1
property_to_net_income_ratio = property_plant_equipment / net_income
if property_to_net_income_ratio < 2:
    buffet_approved += 1
    buffet_approved_summary += '\n-' + _('Tangible fixed assets (PPE) are reasonable: the tangible fixed assets to net income ratio is less than') + ' 2 ({:.2f})'.format(property_to_net_income_ratio)
else:
    buffet_not_approved_summary += '\n-' + _('The tangible fixed assets (PPE) are not very reasonable: the tangible fixed assets to net income ratio is greater than') + ' 2 ({:.2f})'.format(property_to_net_income_ratio)

# # goodwill + intangible assets
# buffet_criterias += 1
# total_debt =  short_term_debt + long_term_debt
# enterprise_value = market_cap + total_debt - cash_and_cash_equivalents
# print('% = {}'.format(((goodwill + intangible_assets) * 100) / enterprise_value))

# capex
if capital_expenditures != None:
    buffet_criterias += 1
    capital_expenditures_to_profit_ratio = np.abs(capital_expenditures, dtype=np.int64) * 100 / net_income
    if capital_expenditures_to_profit_ratio < 50:
        buffet_approved += 1
        buffet_approved_summary += '\n-' + _('Capital expenditures are reasonable, they represent less than 50% of the net income') + ' ({:.2f}%)'.format(capital_expenditures_to_profit_ratio)
    else:
        buffet_not_approved_summary += '\n-' + _('Capital expenditures are not very reasonable, they represent more than 50% of the net income') + ' ({:.2f}%)'.format(capital_expenditures_to_profit_ratio)

# results
if buffet_approved / buffet_criterias >= 0.5 and buffet_approved / buffet_criterias <= 0.7:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('meets some of Warren Buffet\'s selection criteria'))
elif buffet_approved / buffet_criterias > 0.7:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('meets most of Warren Buffet\'s selection criteria'))
else:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('does not meet Warren Buffet\'s selection criteria'))
print('\n' + _('Recommendation') + ' {:.2f}/10'.format(buffet_approved * 10 / buffet_criterias))
print(_('Pros') + ': {}'.format(buffet_approved_summary))
print(_('Cons') + ': {}'.format(buffet_not_approved_summary))

if slater_approved / slater_criterias > 0.5 and slater_approved / slater_criterias < 0.7:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('meets some of Jim Slater\'s selection criteria'))
elif slater_approved / slater_criterias > 0.7:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('meets most of Jim Slater\'s selection criteria'))
else:
    print('\n' + _('The stock value of') + ' {} '.format(company_name) + _('does not meet Jim Slater\'s selection criteria'))
print('\n' + _('Recommendation') + ' {:.2f}/10'.format(slater_approved * 10 / slater_criterias))
print(_('Pros') + ': {}'.format(slater_approved_summary))
print(_('Cons') + ': {}'.format(slater_not_approved_summary))

earnings_table = []
earnings_table_headers = []
for i in range(len(earnings)):
        earnings_table.append(earnings[i]['earnings']['fmt'])
        earnings_table_headers.append(earnings[i]['date'])
printv('\n* ' + _('The change in net income') + ':\n\n+' + tabulate([earnings_table], headers=earnings_table_headers) + '\n')