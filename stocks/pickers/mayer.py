import config
from utils.translate import Translator

class Mayer:
    def __init__(self, equity):
        self.equity = equity

    def __safe_get(self, value, index):
        return None if value is None else value[index]

    def __safe_cast(self, value, to_type):
        try:
            return to_type(value)
        except (ValueError, TypeError):
            return None

    def evaluation(self):
        # get translator
        tr = Translator(config.language)

        # init
        n_approved = 0
        n_evaluated = 0
        approved_summary = ""
        not_approved_summary = ""

        # income statement
        income_statement = self.equity.income_statement

        revenue = self.__safe_get(income_statement.total_revenue(), 0)

        # ratios
        ratios = self.equity.ratios

        annual_price_to_sales_ttm = ratios.price_to_sales_ttm()
        price_to_sales_ratio = self.__safe_cast(self.__safe_get(annual_price_to_sales_ttm, 0), float)

        ## market cap
        market_cap = self.equity.market_cap()

        if market_cap and price_to_sales_ratio:
            n_evaluated += 1
            if (market_cap > 300e6 and market_cap < 700e6) and (revenue > 140e6 and revenue < 200e6) \
                and (price_to_sales_ratio > 2.5 and price_to_sales_ratio < 3.5):
                n_approved += 1
                approved_summary += "\n-" + tr("Mayer may consider this company as a potential 100-bagger provided it has and international expansion potential")
            else:
                not_approved_summary += "\n-" + tr("Mayer may not consider this company as a potential 100-bagger")

        ### results
        if n_evaluated > 0:
            company_name = self.equity.name
            if n_approved / n_evaluated > 0.5 and n_approved / n_evaluated < 0.7:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("meets some of Chris Mayer's selection criteria"))
            elif n_approved / n_evaluated > 0.7:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("meets most of Chris Mayer's selection criteria"))
            else:
                print("\n" + tr("The stock value of") + " {} ".format(company_name) + tr("does not meet Chris Mayer's selection criteria"))
            print("\n" + tr("Recommendation") + " {:.2f}/10".format(n_approved * 10 / n_evaluated))
            print(tr("Pros") + ": {}".format(approved_summary))
            print(tr("Cons") + ": {}".format(not_approved_summary))