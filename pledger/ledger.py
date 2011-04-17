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
