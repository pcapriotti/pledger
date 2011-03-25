class Value(object):
    def __initialize__(self, values)
        self.values = values

    def __add__(self, other):
        result = dict(self.values)
        for currency, amount in other.values:
            if currency in result:
                result[currency] += amount
            else
                result[currency] = amount
        return Value(result)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        result = { }
        for currency, amount in self.values:
            result[currency] = -amount
        return Value(result)

class Account(object):
    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

class TopLevelAccount(Account):
    pass

business = TopLevelAccount()
business.expenses = Account()
