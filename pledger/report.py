from pledger.value import ZERO
from pledger.util import struct, linearized, PrefixTree
from pledger.template import BalanceTemplate, RegisterTemplate
from pledger.ledger_processor import LedgerProcessor

class BalanceEntryProcessor(object):
    Entry = struct("level", "account", "amount")

    def __init__(self):
        self.sheet = { }
        self.total = ZERO

    def process_entry(self, transaction, entry):
        self.add_entry(entry.account, entry.amount)

    def add_entry(self, account, amount):
        self.sheet.setdefault(account, ZERO)
        self.sheet[account] += amount
        if account.parent:
            self.add_entry(account.parent, amount)
        else:
            self.total += amount

    def accounts(self):
        grouped = self.grouped_accounts(None, 0, sorted(self.sheet.keys()))
        root, items = grouped[0]
        return linearized(items)

    def grouped_accounts(self, root, level, accounts, prefix = ""):
        children = [account for account in accounts if account.parent == root]
        if len(children) == 1 and root and root.base_name and self.sheet[root] == self.sheet[children[0]]:
            return self.grouped_accounts(children[0], level, accounts, prefix + root.base_name + ":")
        else:
            result = [self.grouped_accounts(child, level + 1, accounts) for child in children]
            if root:
                return ((root, prefix + str(root.base_name), level), result)
            else:
                return result

    def post_process(self):
        pass

    @property
    def result(self):
        yield self.__class__.Entry(level=None,
                                   account=None,
                                   amount=self.total)
        for account, name, level in self.accounts():
            yield self.__class__.Entry(level=level,
                                       account=name,
                                       amount=self.sheet[account])

class RegisterEntryProcessor(object):
    class Entry(struct("transaction", "entry", "total")):
        @property
        def date(self):
            return self.entry.date(self.transaction)

    def __init__(self, sorting):
        self.unsorted_result = []
        self.total = ZERO
        self.sorting = sorting

    def process_entry(self, transaction, entry):
        e = RegisterEntryProcessor.Entry(
                transaction=transaction,
                entry=entry,
                total=ZERO)
        self.unsorted_result.append(e)

    def post_process(self):
        self.result = self.sorting(self.unsorted_result)
        total = ZERO
        for entry in self.result:
            total += entry.entry.amount
            entry.total = total

class Report(object):
    def __init__(self, ledger, rules, transaction_rules, filter, entry_processor, template):
        self.ledger_processor = LedgerProcessor(ledger, rules, transaction_rules)
        self.ledger_processor.add_listener(self)
        self.filter = filter
        self.entry_processor = entry_processor
        self.template = template

    def generate(self):
        self.ledger_processor.run()
        self.entry_processor.post_process()
        return self.result()

    def on_transaction(self, transaction, entries):
        for entry in entries:
            if self.filter(transaction, entry):
                self.entry_processor.process_entry(transaction, entry)

    def result(self):
        return self.entry_processor.result

    @classmethod
    def balance(cls, ledger, rules, transaction_rules, filter, sorting):
        return cls(ledger, rules, transaction_rules, filter, BalanceEntryProcessor(),
                template=BalanceTemplate())

    @classmethod
    def register(cls, ledger, rules, transaction_rules, filter, sorting):
        return cls(ledger, rules, transaction_rules, filter, RegisterEntryProcessor(sorting),
                template=RegisterTemplate())

class ReportRegistry(object):
    def __init__(self, reps):
        self.reps = reps
        self.prefix_tree = PrefixTree(reps.keys())

    def get(self, prefix):
        candidates = self.prefix_tree.from_prefix(prefix)
        if len(candidates) == 1:
            return self.reps[candidates[0]]

reports = ReportRegistry({
    "balance" : Report.balance,
    "register" : Report.register
})
