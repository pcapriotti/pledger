import unittest
from pledger.entry import Entry
from pledger.ledger_processor import LedgerProcessor
from pledger.parser import Parser
from pledger.rule import RuleCollection
from pledger.value import Value
from tests.fixtures import fixture_path


class TransactionCollector(object):
    def __init__(self):
        self.transactions = []

    def on_transaction(self, transaction, entries):
        self.transactions.append((transaction, entries))


class TestLedgerProcessor(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.rules = RuleCollection()

    def testAccountPrefix(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        processor = LedgerProcessor(ledger, self.rules)
        collector = TransactionCollector()
        processor.add_listener(collector)

        processor.add_account_prefix("Business")
        processor.run()

        for transaction, entries in collector.transactions:
            for entry in entries:
                self.assertEqual("Business", entry.account.root().name)

    def testRemoveAccountPrefix(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        processor = LedgerProcessor(ledger, self.rules)
        collector = TransactionCollector()
        processor.add_listener(collector)

        self.assertEqual(2, len(ledger.transactions))

        processor.add_account_prefix("Business")
        ledger.transactions[0].execute(processor)

        for transaction, entries in collector.transactions:
            for entry in entries:
                self.assertEqual("Business", entry.account.root().name)

        collector.transactions = []
        processor.remove_account_prefix()

        ledger.transactions[0].execute(processor)

        for transaction, entries in collector.transactions:
            for entry in entries:
                self.assertNotEqual("Business", entry.account.root().name)

    def testInclude(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        processor = LedgerProcessor(ledger, self.rules)
        collector = TransactionCollector()
        processor.add_listener(collector)

        processor.run()
        processor.include("extra.dat")

        self.assertEqual(3, len(collector.transactions))

    def testCompact(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        processor = LedgerProcessor(ledger, self.rules)
        entry = ledger.transactions[1].entries[0]
        self.assertEqual(Value.parse("35 EUR"), entry.amount)
        # add entry
        entry2 = Entry(entry.account, Value.parse("-5 EUR"))
        ledger.transactions[1].entries.append(entry2)
        # rebalance transaction
        ledger.transactions[1].entries[1].amount += Value.parse("5 EUR")

        collector = TransactionCollector()
        processor.add_listener(collector)
        processor.run()

        self.assertEqual(2, len(collector.transactions))
        _, entries = collector.transactions[1]
        self.assertEqual(2, len(entries))

        self.assertEqual(Value.parse("30 EUR"), entries[0].amount)
