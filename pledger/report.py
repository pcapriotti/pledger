from pledger.value import ZERO
from pledger.util import struct, linearized

class BalanceEntryProcessor(object):
    Entry = struct("level", "account", "amount")

    def __init__(self):
        self.sheet = { }

    def process_entry(self, transaction, entry):
        self.add_entry(entry.account, entry.amount)

    def add_entry(self, account, amount):
        self.sheet.setdefault(account, ZERO)
        self.sheet[account] += amount
        if account.parent:
            self.add_entry(account.parent, amount)

    def accounts(self):
        grouped = self.__class__.grouped_accounts(None, 0, sorted(self.sheet.keys()))
        root, items = grouped[0]
        return linearized(items)

    @classmethod
    def grouped_accounts(cls, root, level, accounts, prefix = ""):
        children = [account for account in accounts if account.parent == root]
        if len(children) == 1 and root and root.base_name:
            return cls.grouped_accounts(children[0], level, accounts, prefix + root.base_name + ":")
        else:
            result = [cls.grouped_accounts(child, level + 1, accounts) for child in children]
            if root:
                return ((root, prefix + str(root.base_name), level), result)
            else:
                return result

    @property
    def result(self):
        for account, name, level in self.accounts():
            yield self.__class__.Entry(level=level,
                                       account=name,
                                       amount=self.sheet[account])

class RegisterEntryProcessor(object):
    Entry = struct("date", "label", "account", "amount", "total")

    def __init__(self, sorting):
        self.unsorted_result = []
        self.total = ZERO
        self.sorting = sorting

    def process_entry(self, transaction, entry):
        self.total += entry.amount
        e = RegisterEntryProcessor.Entry(
                date=transaction.date,
                label=transaction.label,
                account=entry.account,
                amount=entry.amount,
                total=self.total)
        self.unsorted_result.append(e)

    @property
    def result(self):
        l = list(self.unsorted_result)
        self.sorting.apply_to(l)
        return l

class Report(object):
    def __init__(self, ledger, rules, filter, entry_processor):
        self.ledger_processor = ledger.create_processor(rules)
        self.ledger_processor.add_listener(self)
        self.filter = filter
        self.entry_processor = entry_processor

    def generate(self):
        self.ledger_processor.run()
        return self.result()

    def on_transaction(self, transaction, entries):
        for entry in entries:
            if self.filter(transaction, entry):
                self.entry_processor.process_entry(transaction, entry)

    def result(self):
        return self.entry_processor.result

    @classmethod
    def balance(cls, ledger, rules, filter, sorting):
        return cls(ledger, rules, filter, BalanceEntryProcessor())

    @classmethod
    def register(cls, ledger, rules, filter, sorting):
        return cls(ledger, rules, filter, RegisterEntryProcessor(sorting))

reports = {
    "balance" : Report.balance,
    "register" : Report.register
}
