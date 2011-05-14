from pledger.value import ZERO
from pledger.entry import Entry
from pledger.filters import FilterCollection

class LedgerProcessor(object):
    def __init__(self, ledger, filters = None):
        self.ledger = ledger
        self.account_prefix = ""
        self.total = ZERO
        self.filters = filters or FilterCollection()

    def run(self):
        for transaction in self.ledger.transactions:
            transaction.execute(self)

    def add_account_prefix(self, prefix):
        self.account_prefix += prefix

    def add_transaction(self, transaction):
        entries = self.filter(transaction)
        for entry in entries:
            self.total += entry.amount
        self.process_entries(transaction, entries)

    def process_entries(self, transaction, entries):
        pass

    def filter(self, transaction):
        result = []
        for entry in transaction.entries:
            account = entry.account.add_prefix(self.account_prefix)
            amount = entry.amount
            if self.filters:
                result += self.filters.apply(transaction, account, amount)
        return result
