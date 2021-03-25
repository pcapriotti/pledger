from pledger.entry import Entry
from pledger.ledger_processor import LedgerProcessor
from pledger.parser import Parser
from pledger.rule import RuleCollection
from pledger.value import Value

import pytest

@pytest.fixture
def rules():
    return RuleCollection()

class TransactionCollector(object):
    def __init__(self):
        self.transactions = []

    def on_transaction(self, transaction, entries):
        self.transactions.append((transaction, entries))


def test_account_prefix(parser, rules):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    processor = LedgerProcessor(ledger, rules)
    collector = TransactionCollector()
    processor.add_listener(collector)

    processor.add_account_prefix("Business")
    processor.run()

    for transaction, entries in collector.transactions:
        for entry in entries:
            assert entry.account.root().name == "Business"

def test_remove_account_prefix(parser, rules):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    processor = LedgerProcessor(ledger, rules)
    collector = TransactionCollector()
    processor.add_listener(collector)

    assert len(ledger.transactions) == 2

    processor.add_account_prefix("Business")
    ledger.transactions[0].execute(processor)

    for transaction, entries in collector.transactions:
        for entry in entries:
            assert entry.account.root().name == "Business"

    collector.transactions = []
    processor.remove_account_prefix()

    ledger.transactions[0].execute(processor)

    for transaction, entries in collector.transactions:
        for entry in entries:
            assert entry.account.root().name != "Business"

def test_include(parser, rules):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    processor = LedgerProcessor(ledger, rules)
    collector = TransactionCollector()
    processor.add_listener(collector)

    processor.run()
    processor.include("extra.dat")

    assert len(collector.transactions) == 3

def test_compact(parser, rules):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    processor = LedgerProcessor(ledger, rules)
    entry = ledger.transactions[1].entries[0]
    assert entry.amount == Value.parse("35 EUR")
    # add entry
    entry2 = Entry(entry.account, Value.parse("-5 EUR"))
    ledger.transactions[1].entries.append(entry2)
    # rebalance transaction
    ledger.transactions[1].entries[1].amount += Value.parse("5 EUR")

    collector = TransactionCollector()
    processor.add_listener(collector)
    processor.run()

    assert len(collector.transactions) == 2
    _, entries = collector.transactions[1]
    assert len(entries) == 2

    assert entries[0].amount == Value.parse("30 EUR")
