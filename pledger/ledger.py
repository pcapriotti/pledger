from pledger.transaction import Transaction
from pledger.ledger_processor import LedgerProcessor
import itertools
import util

class Ledger(object):
    def __init__(self, transactions, parser):
        self.transactions = transactions
        self.parser = parser

    def all_matching(self, predicate):
        return itertools.ifilter(predicate, self.entries)

    def add(self, transaction):
        self.transactions.append(transaction)

    def create_processor(self, rules):
        return LedgerProcessor(self, rules)

    @property
    def entries(self):
        return itertools.chain(*self.transactions)
