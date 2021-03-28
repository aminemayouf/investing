import config
from utils.translate import Translator

class Slater:

    def __init__(self, equity):
        self.equity = equity

    def __safe_get(self, value, index):
        return None if value is None else value[index]

    def evaluation(self):
        # get translator
        tr = Translator(config.language)

        # init
        n_approved = 0
        n_evaluated = 0
        approved_summary = ""
        not_approved_summary = ""

        ## market cap
        market_cap = self.equity.market_cap()

        if market_cap:
            n_evaluated += 1
            if market_cap > 300e6 and market_cap < 2e9:
                n_approved += 1
                approved_summary += "\n-" + tr("Slater likes smallcaps")
            else:
                not_approved_summary += "\n-" + tr("Slater prefers smallcaps")

        # income statement
        income_statement = self.equity.income_statement

        annual_net_income = income_statement.net_income()
        ebit = self.__safe_get(income_statement.net_income_before_taxes(), 0)

        # earnings trend
        n_evaluated += 1
        earnings_growth = 0
        n = len(annual_net_income)
        for i in reversed(range(1, n-1)):
            sign = +1
            if annual_net_income[i-1] > annual_net_income[i]:
                sign = -1
            earnings_growth += sign * (1 - (annual_net_income[i-1] / annual_net_income[i])) * 100

        earnings_growth /= n
        if earnings_growth > 15:
            n_approved += 1
            approved_summary += "\n-" + tr("The annual earnings growth rate is higher than") + " 15% ({:.2f}%)".format(earnings_growth)
        else:
            not_approved_summary += "\n-" + tr("The annual earnings growth rate is lower than") + " 15% ({:.2f}%)".format(earnings_growth)

        ## balance sheet
        balance_sheet = self.equity.balance_sheet

        accounts_receivable = self.__safe_get(balance_sheet.accounts_receivable(), 0)
        cash_and_cash_equivalents = self.__safe_get(balance_sheet.cash_and_equivalents(), 0)
        current_liabilities = self.__safe_get(balance_sheet.total_current_liabilities(), 0)
        other_short_term_investments = self.__safe_get(balance_sheet.short_term_investments(), 0)
        total_assets = self.__safe_get(balance_sheet.total_assets(), 0)

        ## overall financial performance
        # roce (return on capital employed)
        if total_assets and current_liabilities and ebit:
            n_evaluated += 1
            capital_employed = total_assets - current_liabilities
            roce = ebit / capital_employed * 100
            if roce > 20:
                n_approved += 1
                approved_summary += "\n-" + tr("The return on capital employed is higher than") + " 20% ({:.2f}%)".format(roce)
            else:
                not_approved_summary += "\n-" + tr("The return on capital employed is lower than") + " 20% ({:.2f}%)".format(roce)

        # quick ratio
        if other_short_term_investments and accounts_receivable and cash_and_cash_equivalents and current_liabilities:
            n_evaluated += 1
            quick_ratio = (cash_and_cash_equivalents + other_short_term_investments + accounts_receivable) / current_liabilities
            if quick_ratio > 1:
                n_approved += 1
                approved_summary += "\n-" + tr("The company has good financials, it's QR is higher than") + " 1 ({:.2f})".format(quick_ratio)
            else: 
                not_approved_summary += "\n-" + tr("The company doesn't have good financials, it's QR is lower than") + " 1 ({:.2f})".format(quick_ratio)

        ### results
        if n_evaluated > 0:
            company_name = self.equity.name
            if n_approved / n_evaluated > 0.5 and n_approved / n_evaluated < 0.7:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("meets some of Jim Slater's selection criteria"))
            elif n_approved / n_evaluated > 0.7:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("meets most of Jim Slater's selection criteria"))
            else:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("does not meet Jim Slater's selection criteria"))
            print("\n" + tr("Recommendation") + " {:.2f}/10".format(n_approved * 10 / n_evaluated))
            print(tr("Pros") + ": {}".format(approved_summary))
            print(tr("Cons") + ": {}".format(not_approved_summary))
