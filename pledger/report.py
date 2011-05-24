from pledger.listeners import BalanceListener

class Report(object):
    pass

class BalanceReport(Report):
    def __init__(self, ledger, filters):
        self.processor = ledger.create_processor(filters)
        self.balance = BalanceListener()

        self.processor.add_listener(self.balance)

    def generate(self):
        self.processor.run()
        return self.balance.total

class RegisterReport(Report):
    class Entry(object):
        def __init__(self, date, label, account, amount, total):
            self.date = date
            self.label = label
            self.account = account
            self.amount = amount
            self.total = total

    def __init__(self, ledger, filters, grouping = None):
        self.processor = ledger.create_processor(filters)
        self.balance = BalanceListener()

        self.processor.add_listener(self.balance)
        self.processor.add_listener(self)

        self.entries = []

    def generate(self):
        self.processor.run()
        return self.entries

    def on_transaction(self, transaction, entries):
        for entry in entries:
            entry = RegisterReport.Entry(transaction.date,
                                         transaction.label,
                                         entry.account,
                                         entry.amount,
                                         self.balance.total)
            self.entries.append(entry)
