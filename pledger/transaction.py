from .value import ZERO
from .directive import Directive
from .util import PledgerException
from .tags import TagFilterable

class UnbalancedTransaction(PledgerException):
    def __init__(self, tr):
        self.tr = tr
        super(UnbalancedTransaction, self).__init__()

class UndefinedTransaction(PledgerException):
    def __init__(self, tr, index):
        self.tr = tr
        self.index = index
        super(UndefinedTransaction, self).__init__()

class Transaction(TagFilterable):
    def __init__(self, entries, date = None, label = "", tags = None):
        super(Transaction, self).__init__()
        self.entries = entries
        self.date = date
        self.label = label
        if tags: self.tags = tags
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

    @classmethod
    def from_entry(cls, transaction, entry):
        return transaction

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

    def clone(self):
        return self.__class__(self.entries, self.date, self.label, self.tags)

    @classmethod
    def account_tag_filter(cls, tag, value=None):
        def get_taggables(transaction, entry):
            return [e.account for e in transaction.entries]
        return cls.general_tag_filter(get_taggables, tag, value)
