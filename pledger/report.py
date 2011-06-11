from pledger.value import ZERO
from pledger.util import struct, linearized
from pledger.template import BalanceTemplate, RegisterTemplate

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
    Entry = struct("transaction", "entry", "total")

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
        self.result = self.sorting.apply_to(self.unsorted_result)
        total = ZERO
        for entry in self.result:
            total += entry.entry.amount
            entry.total = total

class Report(object):
    def __init__(self, ledger, rules, filter, entry_processor, template):
        self.ledger_processor = ledger.create_processor(rules)
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
    def balance(cls, ledger, rules, filter, sorting):
        return cls(ledger, rules, filter, BalanceEntryProcessor(),
                template=BalanceTemplate())

    @classmethod
    def register(cls, ledger, rules, filter, sorting):
        return cls(ledger, rules, filter, RegisterEntryProcessor(sorting),
                template=RegisterTemplate())

reports = {
    "balance" : Report.balance,
    "register" : Report.register
}
