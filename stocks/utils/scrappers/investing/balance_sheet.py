
class BalanceSheet:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data.to_string()

    def current_debt_and_capital_lease_obligation(self):
        return self.data.loc["Current Port. of LT Debt/Capital Leases"]

    def total_common_shares_outstanding(self):
        return self.data.loc["Total Common Shares Outstanding"]
