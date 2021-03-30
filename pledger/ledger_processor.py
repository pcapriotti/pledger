from .account import Account, AccountFactory
from .value import ZERO
from .entry import Entry
from .transaction import Transaction
from .util import Observable
from collections import OrderedDict


class LedgerProcessor(Observable):
    def __init__(self, parser, rules):
        super(LedgerProcessor, self).__init__()
        self.rules = rules
        self.parser = parser
        self.account = self.parser.repo.root()
        self.ledger = None

    def run(self, ledger):
        self.ledger = ledger
        for transaction in self.ledger.transactions:
            transaction.execute(self)

    def add_account_prefix(self, prefix):
        self.account = self.account[prefix]

    def remove_account_prefix(self):
        self.account = self.account.parent

    def add_transaction(self, transaction):
        entries = self.filter(transaction)
        t = self.process_transaction(transaction, entries)
        self.fire("transaction", t, entries)

    def include(self, filename):
        filename = self.ledger.absolute_filename(filename)
        subledger = self.parser.parse_ledger(filename)
        self.create_child().run(subledger)

    def filter(self, transaction):
        result = []
        for entry in transaction.entries:
            entry = Entry(self.account.sub(entry.account.path),
                          entry.amount,
                          entry.tags)
            result += self.rules.apply(transaction, entry)
        return self.compact(result)

    def process_transaction(self, transaction, entries):
        return Transaction(entries, transaction.date, transaction.label, transaction.tags)

    def create_child(self):
        child = self.__class__(self.parser, self.rules)
        child.account = self.account
        child.listeners = self.listeners
        return child

    def compact(self, entries):
        result = OrderedDict()
        for entry in entries:
            key = (entry.account.path, tuple(sorted(entry.tags.items())))
            e = result.get(key)
            if e:
                e.amount += entry.amount
            else:
                result[key] = entry.clone()
        return list(result.values())
