
class BalanceSheet:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data.to_string()

    def total_common_shares_outstanding(self):
        return self.data.loc["Total Common Shares Outstanding"]
