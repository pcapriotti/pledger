from pledger.entry import Entry
from pledger.value import ZERO
from pledger.directive import Directive

class UnbalancedTransaction(Exception):
    def __init__(self, tr):
        self.tr = tr

class UndefinedTransaction(Exception):
    def __init__(self, tr):
        self.tr = tr

class Transaction(object):
    def __init__(self, entries):
        self.entries = entries
        undef = None
        balance = ZERO
        for e in self.entries:
            if e.amount is None:
                if undef: raise UndefinedTransaction(self)
                undef = e
            else:
                balance += e.amount
        if undef:
            undef.amount = -balance
        elif not balance.null():
            raise UnbalancedTransaction(self)

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

    @classmethod
    def parse(cls, str):
        if hasattr(str, "split"):
            lines = iter(str.split("\n"))
        else:
            lines = iter(str)
        header = lines.next()

        directive = Directive.parse(header)
        if directive: return directive

        entries = [Entry.parse(line) for line in lines]
        return Transaction(entries)
