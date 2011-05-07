class LedgerProcessor(object):
    def __init__(self, ledger):
        self.ledger = ledger
        self.account_prefix = ""

    def run(self):
        for transaction in self.ledger.transactions:
            transaction.execute(self)

    def add_account_prefix(self, prefix):
        self.account_prefix += prefix

    def add_transaction(self, transaction):
        pass

