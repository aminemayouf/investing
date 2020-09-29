
class IncomeStatement:

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data.to_string()
