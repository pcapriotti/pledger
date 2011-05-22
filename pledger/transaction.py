import re
from pledger.entry import Entry
from pledger.value import ZERO
from pledger.directive import Directive

class UnbalancedTransaction(Exception):
    def __init__(self, tr):
        self.tr = tr

class UndefinedTransaction(Exception):
    def __init__(self, tr, index):
        self.tr = tr
        self.index = index

class Transaction(object):
    def __init__(self, entries):
        self.entries = entries
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
            lines = itertools.izip(itertools.count(1), iter(str.split("\n")))
        else:
            lines = iter(str)
        lines = ((n, line) for (n, line) in lines if not re.match("\s*;", line))
        n, header = lines.next()

        directive = Directive.parse(header)
        if directive: return directive

        entries = [Entry.parse(line) for n, line in lines]
        line_numbers = [n for n, line in lines]
        try:
            return Transaction(entries)
        except UnbalancedTransaction, e:
            e.line_number = n
        except UndefinedTransaction, e:
            e.line_number = line_numbers[e.index]
