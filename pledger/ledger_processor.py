from pledger.value import ZERO
from pledger.entry import Entry
from pledger.filters import FilterCollection
from pledger.util import Observable

class LedgerProcessor(Observable):
    def __init__(self, ledger, filters = None):
        super(LedgerProcessor, self).__init__()
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
        self.fire("transaction", transaction, entries)
        for entry in entries:
            self.total += entry.amount

    def filter(self, transaction):
        result = []
        for entry in transaction.entries:
            account = entry.account.add_prefix(self.account_prefix)
            amount = entry.amount
            if self.filters:
                result += self.filters.apply(transaction, account, amount)
        return result
