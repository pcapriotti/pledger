from dataclasses import dataclass, field, replace

from .value import ZERO
from .directive import Directive
from .util import PledgerException


class UnbalancedTransaction(PledgerException):
    def __init__(self, tr):
        self.tr = tr
        super(UnbalancedTransaction, self).__init__()


class UndefinedTransaction(PledgerException):
    def __init__(self, tr, index):
        self.tr = tr
        self.index = index
        super(UndefinedTransaction, self).__init__()


@dataclass
class Transaction:
    entries: list
    date: object = None
    label: str = ""
    tags: dict = field(default_factory=dict)

    @classmethod
    def balanced(cls, *args, **kwargs):
        self = cls(*args, **kwargs)

        undef = None
        balance = ZERO
        for i, e in enumerate(self.entries):
            if e.amount is None:
                if undef:
                    raise UndefinedTransaction(self, i)
                undef = e
            else:
                balance += e.amount
        if undef:
            undef.amount = -balance
        elif not balance.null():
            raise UnbalancedTransaction(self)

        return self

    def execute(self, processor):
        processor.add_transaction(self)

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

    def clone(self):
        return replace(self)
