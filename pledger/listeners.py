from pledger.util import Observable
from pledger.value import ZERO

class BalanceListener(Observable):
    def __init__(self):
        super(BalanceListener, self).__init__()
        self.total = ZERO

    def on_transaction(self, transaction, entries):
        for entry in entries:
            self.total += entry.amount
        self.fire("transaction_total", self.total)
