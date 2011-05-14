from pledger.value import ZERO

class LedgerProcessor(object):
    def __init__(self, ledger, filters = None):
        self.ledger = ledger
        self.account_prefix = ""
        self.total = ZERO
        self.filters = filters

    def run(self):
        for transaction in self.ledger.transactions:
            transaction.execute(self)

    def add_account_prefix(self, prefix):
        self.account_prefix += prefix

    def add_transaction(self, transaction):
        entries = self.filter(transaction)
        for entry in entries:
            self.total += entry.amount
        self.process_entries(entries)

    def process_entries(self, entries):
        pass

    def filter(self, transaction):
        return transaction.entries
