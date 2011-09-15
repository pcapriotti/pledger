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
from decimal import Decimal
from pledger.account import Account
from pledger.filter import Filter
from pledger.parser import Parser
from pledger.rule import Rule, RuleCollection, Generator
from pledger.transaction import Transaction
from tests.fixtures import fixture_path

class RuleTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.bank_account = self.parser.parse_account("Assets:Bank")
        self.books_account = self.parser.parse_account("Expenses:Books")
        self.cash_account = self.parser.parse_account("Assets:Cash")

        bank = self.bank_account - self.parser.parse_value("33 EUR")
        books = self.books_account + self.parser.parse_value("33 EUR")
        self.tr = Transaction([bank, books])

        self.rules = RuleCollection()

        @Generator
        def discount(entry):
            amount = entry.amount * Decimal("0.1")
            yield entry.account - amount
            yield self.cash_account + amount
        self.discount = discount

    def testRuleOnLedger(self):
        rule = Rule(Filter.has_account(self.books_account), self.discount)
        self.rules.add_rule(rule)

        result = []
        result += self.rules.apply(self.tr, self.tr.entries[0])
        result += self.rules.apply(self.tr, self.tr.entries[1])

        expected = [self.bank_account - self.parser.parse_value("33.00 EUR"),
                    self.books_account + self.parser.parse_value("33.00 EUR"),
                    self.cash_account + self.parser.parse_value("3.30 EUR"),
                    self.books_account - self.parser.parse_value("3.30 EUR")]

        self.assertItemsEqual(expected, result)

    def testAccountTagRule(self):
        self.books_account.tags["discount"] = self.discount
        self.rules.add_rule(Account.tag_rule("discount"))

        result = []
        result += self.rules.apply(self.tr, self.tr.entries[0])
        result += self.rules.apply(self.tr, self.tr.entries[1])

        expected = [self.bank_account - self.parser.parse_value("33.00 EUR"),
                    self.books_account + self.parser.parse_value("33.00 EUR"),
                    self.cash_account + self.parser.parse_value("3.30 EUR"),
                    self.books_account - self.parser.parse_value("3.30 EUR")]

        self.assertItemsEqual(expected, result)

class GeneratorTest(unittest.TestCase):
    def testNullGenerator(self):
        g = Generator.null
        transaction = object()
        entry = object()

        self.assertEqual([], list(g(transaction, entry)))

    def testGeneratorSum(self):
        @Generator
        def g1(transaction, entry):
            yield entry

        @Generator
        def g2(transaction, entry):
            yield entry
            yield entry

        g = g1 + g2
        transaction = object()
        entry = object()

        self.assertEqual(3, len(list(g(transaction, entry))))
