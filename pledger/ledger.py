from pledger.transaction import Transaction
from pledger.ledger_processor import LedgerProcessor
import itertools
import util

class Ledger(object):
    def __init__(self, transactions):
        self.transactions = transactions

    def all_matching(self, predicate):
        return itertools.ifilter(predicate, self.entries)

    def add(self, transaction):
        self.transactions.append(transaction)

    def create_processor(self, filters = None):
        return LedgerProcessor(self, filters)

    @property
    def entries(self):
        return itertools.chain(*self.transactions)

    @classmethod
    def parse(self, str):
        f = lambda (number, line): line == ""

        lines = itertools.izip(itertools.count(1), str.split("\n"))
        transactions = [Transaction.parse(group) for group in util.itersplit(f, lines)]
        return Ledger(transactions)
