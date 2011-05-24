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

class MalformedHeader(Exception):
    pass

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

    @classmethod
    def parse(cls, str):
        if hasattr(str, "split"):
            lines = itertools.izip(itertools.count(1), iter(str.split("\n")))
        else:
            lines = iter(str)
        lines = ((n, line) for (n, line) in lines if not re.match("\s*;", line))
        try:
            n, header = lines.next()
        except StopIteration:
            return None

        directive = Directive.parse(header)
        if directive: return directive

        try:
            date, label = cls.parse_header(header)
            entries = [Entry.parse(line) for n, line in lines]
            line_numbers = [n for n, line in lines]
            return Transaction(entries, date, label)
        except UnbalancedTransaction, e:
            e.line_number = n
        except UndefinedTransaction, e:
            e.line_number = line_numbers[e.index]
        except MalformedHeader, e:
            e.line_number = n

    @classmethod
    def parse_header(cls, str):
        m = re.match(r'^(\S+)\s+(\*?\s+)(.*)$', str)
        if m:
            return m.group(1), m.group(3)
        else:
            raise MalformedHeader()
