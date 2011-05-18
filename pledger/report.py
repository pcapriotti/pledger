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
