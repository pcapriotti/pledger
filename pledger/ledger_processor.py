from pledger.value import ZERO
from pledger.entry import Entry
from pledger.util import Observable

class LedgerProcessor(Observable):
    def __init__(self, ledger, rules):
        super(LedgerProcessor, self).__init__()
        self.ledger = ledger
        self.rules = rules
        self.parser = self.ledger.parser
        self.account = self.parser.accounts

    def run(self):
        for transaction in self.ledger.transactions:
            transaction.execute(self)

    def add_account_prefix(self, prefix):
        self.account = self.account[prefix]

    def remove_account_prefix(self):
        self.account = self.account.parent

    def add_transaction(self, transaction):
        entries = self.filter(transaction)
        self.fire("transaction", transaction, entries)

    def include(self, filename):
        filename = self.ledger.absolute_filename(filename)
        subledger = self.parser.parse_ledger(filename)
        self.create_child(subledger).run()

    def filter(self, transaction):
        result = []
        for entry in transaction.entries:
            account = self.account[entry.account.name]
            amount = entry.amount
            result += self.rules.apply(transaction, Entry(account, amount, tags=entry.tags))
        return self.compact(result)

    def create_child(self, ledger):
        child = self.__class__(ledger, self.rules)
        child.account = self.account
        child.listeners = self.listeners
        return child

    def compact(self, entries):
        result = { }
        for entry in entries:
            key = (entry.account, tuple(sorted(entry.tags.items())))
            e = result.get(key)
            if e:
                e.amount += entry.amount
            else:
                result[key] = Entry(entry.account, entry.amount, entry.tags)
        return result.values()
