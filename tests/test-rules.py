import unittest
from decimal import Decimal
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

    def testRuleOnLedger(self):
        @Generator
        def discount(entry):
            amount = entry.amount * Decimal("0.1")
            yield entry.account - amount
            yield self.cash_account + amount

        rule = Rule(Filter.has_account(self.books_account), discount)
        self.rules.add_rule(rule)

        result = []
        result += self.rules.apply(self.tr, self.tr.entries[0])
        result += self.rules.apply(self.tr, self.tr.entries[1])

        expected = [self.bank_account - self.parser.parse_value("33.00 EUR"),
                    self.books_account + self.parser.parse_value("33.00 EUR"),
                    self.cash_account + self.parser.parse_value("3.30 EUR"),
                    self.books_account - self.parser.parse_value("3.30 EUR")]

        self.assertItemsEqual(expected, result)
