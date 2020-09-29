
class BalanceSheet:

    def __init__(self, data):
        self.data = data

    def total_common_shares_outstanding(self):
        return int(float(self.data.loc["Total Common Shares Outstanding"][0])*1e6)
