import itertools
from decimal import Decimal

class Value(object):
    def __init__(self, values):
        self.values = values

    def __add__(self, other):
        result = dict(self.values)
        for currency in other.values:
            amount = other.values[currency]
            if currency in result:
                result[currency] += amount
            else:
                result[currency] = amount
        return Value(result)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        result = { }
        for currency in self.values:
            result[currency] = -self.values[currency]
        return Value(result)

    def format_value(self, curr, value, places=2):
        q = Decimal(10) ** -places      # 2 places --> '0.01'
        sign, digits, exp = value.quantize(q).as_tuple()
        result = []
        digits = map(str, digits)
        build, next = result.append, digits.pop
        build(" " + curr)
        for i in range(places):
            build(next() if digits else '0')
        build('.')
        if not digits:
            build('0')
        i = 0
        while digits:
            build(next())
            i += 1
            if i == 3 and digits:
                i = 0
                build(sep)
        if sign: build('-')
        return ''.join(reversed(result))

    def __str__(self, places=2):
        return ", ".join([self.format_value(curr, value) for
                          curr, value in self.values.iteritems()])

ZERO = Value({})

class Account(object):
    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

class TopLevelAccount(Account):
    pass

class Transaction(object):
    def __init__(self, entries):
        self.entries = entries

    @property
    def amount(self):
        result = ZERO
        for entry in self.entries:
            result += entry.amount
        return result

    def __getitem__(self, i):
        return self.entries[i]

class Entry(object):
    def __init__(self, account, amount):
        self.account = account
        self.amount = amount

class Ledger(object):
    def __init__(self):
        self.transactions = []

    def all_matching(self, predicate):
        return itertools.ifilter(predicate, self.entries)

    def add(self, transaction):
        self.transactions.append(transaction)

    @property
    def entries(self):
        return itertools.chain(*self.transactions)

class Report(object):
    pass

class BalanceReport(Report):
    def __init__(self, ledger, predicate):
        self.ledger = ledger
        self.predicate = predicate

    @property
    def value(self):
        result = ZERO
        for transaction in ledger.all_matching(self.predicate):
            result += transaction.amount
        return result

# example
business = TopLevelAccount()
business.expenses = Account()
business.assets = Account()

ledger = Ledger()
entry1 = business.assets - Value({'EUR': Decimal("10.02") })
entry2 = business.expenses + Value({'EUR': Decimal("10.002") })
ledger.add(Transaction([entry1, entry2]))

report = BalanceReport(ledger, lambda e: e.account == business.expenses)
print report.value
