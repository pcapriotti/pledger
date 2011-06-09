from pledger.entry import Entry
from pledger.value import ZERO
from pledger.directive import Directive
from pledger.util import PledgerException

class UnbalancedTransaction(PledgerException):
    def __init__(self, tr):
        self.tr = tr
        super(UnbalancedTransaction, self).__init__()

class UndefinedTransaction(PledgerException):
    def __init__(self, tr, index):
        self.tr = tr
        self.index = index
        super(UndefinedTransaction, self).__init__()

class Transaction(object):
    def __init__(self, entries, date = None, label = ""):
        self.entries = entries
        self.date = date
        self.label = label
        undef = None
        balance = ZERO
        i = 0
        for e in self.entries:
            if e.amount is None:
                if undef: raise UndefinedTransaction(self, i)
                undef = e
            else:
                balance += e.amount
            i += 1
        if undef:
            undef.amount = -balance
        elif not balance.null():
            raise UnbalancedTransaction(self)

    def execute(self, processor):
        processor.add_transaction(self)

    def __repr__(self):
        return "Transaction (%s)" % self.date

    @property
    def amount(self):
        result = ZERO
        for entry in self.entries:
            result += entry.amount
        return result

    def __getitem__(self, i):
        return self.entries[i]

    def __eq__(self, other):
        return self.entries == other.entries
