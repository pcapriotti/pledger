from pledger.value import ZERO

class BalanceEntryProcessor(object):
    def __init__(self):
        self.result = ZERO

    def process_entry(self, transaction, entry):
        self.result += entry.amount

class RegisterEntryProcessor(object):
    class Entry(object):
        def __init__(self, date, label, account, amount, total):
            self.date = date
            self.label = label
            self.account = account
            self.amount = amount
            self.total = total

    def __init__(self):
        self.result = []
        self.balance = BalanceEntryProcessor()

    def process_entry(self, transaction, entry):
        self.balance.process_entry(transaction, entry)
        e = RegisterEntryProcessor.Entry(
                transaction.date,
                transaction.label,
                entry.account,
                entry.amount,
                self.balance.result)
        self.result.append(e)

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
    def balance(cls, ledger, rules, filter):
        return cls(ledger, rules, filter, BalanceEntryProcessor())

    @classmethod
    def register(cls, ledger, rules, filter):
        return cls(ledger, rules, filter, RegisterEntryProcessor())
