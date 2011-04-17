import itertools

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
if __name__ == '__main__':
    business = TopLevelAccount()
    business.expenses = Account()
    business.assets = Account()

    ledger = Ledger()
    entry1 = business.assets - Value({'EUR': Decimal("10.02") })
    entry2 = business.expenses + Value({'EUR': Decimal("10.002") })
    ledger.add(Transaction([entry1, entry2]))

    report = BalanceReport(ledger, lambda e: e.account == business.expenses)
    print report.value
