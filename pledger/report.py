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
