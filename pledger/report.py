class Report(object):
    pass

class BalanceReport(Report):
    def __init__(self, ledger, filters):
        self.processor = ledger.process(filters)
        self.processor.add_listener(self)

    def on_transaction(self, transaction, entries):
        pass

    def generate(self):
        self.processor.run()
        return self.processor.total
