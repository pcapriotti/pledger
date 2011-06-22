from pledger.transaction import Transaction
from pledger.ledger_processor import LedgerProcessor
import itertools
import os.path

class Ledger(object):
    def __init__(self, filename, transactions, parser):
        self.filename = filename
        self.transactions = transactions
        self.parser = parser

    def all_matching(self, predicate):
        return itertools.ifilter(predicate, self.entries)

    def add(self, transaction):
        self.transactions.append(transaction)

    def absolute_filename(self, filename):
        if os.path.isabs(filename): return filename
        dir = os.path.dirname(self.filename)
        return os.path.join(dir, filename)

    @property
    def entries(self):
        return itertools.chain(*self.transactions)
