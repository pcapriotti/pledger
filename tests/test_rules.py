from decimal import Decimal
from pledger.account import Account, AccountFactory
from pledger.filter import Filter
from pledger.parser import Parser
from pledger.rule import Rule, RuleCollection, Generator
from pledger.transaction import Transaction

class TestRules:
    def setup_method(self):
        self.parser = Parser()
        self.bank_account = self.parser.parse_account("Assets:Bank")
        self.books_account = self.parser.parse_account("Expenses:Books")
        self.cash_account = self.parser.parse_account("Assets:Cash")

        bank = self.bank_account - self.parser.parse_value("33 EUR")
        books = self.books_account + self.parser.parse_value("33 EUR")
        self.tr = Transaction.balanced([bank, books])

        self.rules = RuleCollection()

        @Generator
        def discount(entry):
            amount = entry.amount * Decimal("0.1")
            yield entry.account - amount
            yield self.cash_account + amount
        self.discount = discount

    def test_rule_on_ledger(self):
        rule = Rule(Filter.has_account(self.books_account), self.discount)
        self.rules.add_rule(rule)

        result = []
        result += self.rules.apply(self.tr, self.tr.entries[0])
        result += self.rules.apply(self.tr, self.tr.entries[1])

        expected = [self.bank_account - self.parser.parse_value("33.00 EUR"),
                    self.books_account + self.parser.parse_value("33.00 EUR"),
                    self.cash_account + self.parser.parse_value("3.30 EUR"),
                    self.books_account - self.parser.parse_value("3.30 EUR")]

        assert set((entry.account.path, entry.amount) for entry in result) \
            == set((entry.account.path, entry.amount) for entry in expected)

    def test_account_tag_rule(self):
        self.books_account.tags['discount'] = self.discount
        self.rules.add_rule(Account.tag_rule("discount"))

        result = []
        result += self.rules.apply(self.tr, self.tr.entries[0])
        result += self.rules.apply(self.tr, self.tr.entries[1])

        expected = [self.bank_account - self.parser.parse_value("33.00 EUR"),
                    self.books_account + self.parser.parse_value("33.00 EUR"),
                    self.cash_account + self.parser.parse_value("3.30 EUR"),
                    self.books_account - self.parser.parse_value("3.30 EUR")]

        assert set((entry.account.path, entry.amount) for entry in result) \
            == set((entry.account.path, entry.amount) for entry in expected)

def test_null_generator():
    g = Generator.null
    transaction = object()
    entry = object()

    assert list(g(transaction, entry)) == []

def test_generator_sum():
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

    assert len(list(g(transaction, entry))) == 3
