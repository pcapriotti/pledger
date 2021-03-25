from .transaction import Transaction
from .ledger_processor import LedgerProcessor
import itertools
import os.path

class Ledger(object):
    def __init__(self, filename, transactions, parser):
        self.filename = filename
        self.transactions = transactions
        self.parser = parser

    def absolute_filename(self, filename):
        if os.path.isabs(filename): return filename
        dir = os.path.dirname(self.filename)
        return os.path.join(dir, filename)
