# Copyright (C) 2011 by Paolo Capriotti <p.capriotti@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
        self.trules = []

    def testAccountPrefix(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        processor = LedgerProcessor(ledger, self.rules, self.trules)
        collector = TransactionCollector()
        processor.add_listener(collector)

        processor.add_account_prefix("Business")
        processor.run()

        for transaction, entries in collector.transactions:
            for entry in entries:
                self.assertEqual("Business", entry.account.root().name)

    def testRemoveAccountPrefix(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        processor = LedgerProcessor(ledger, self.rules, self.trules)
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
        processor = LedgerProcessor(ledger, self.rules, self.trules)
        collector = TransactionCollector()
        processor.add_listener(collector)

        processor.run()
        processor.include("extra.dat")

        self.assertEqual(3, len(collector.transactions))

    def testCompact(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        processor = LedgerProcessor(ledger, self.rules, self.trules)
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
