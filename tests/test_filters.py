import unittest
import re
from dataclasses import dataclass
from datetime import date
from pledger.account import Account
from pledger.entry import Entry
from pledger.filter import *
from pledger.parser import Parser
from pledger.transaction import Transaction
import pytest

three_entries = Filter(lambda tr, entry: len(tr.entries) == 3)
in_euro = Filter(lambda tr, entry: list(entry.amount.currencies()) == ["EUR"])

@pytest.fixture
def transactions(parser):
    bank_account = parser.parse_account("Assets:Bank")
    books_account = parser.parse_account("Expenses:Books")
    cash_account = parser.parse_account("Assets:Cash")

    bank = bank_account - parser.parse_value("33 EUR")
    books = books_account + parser.parse_value("33 EUR")
    tr1 = Transaction([bank, books])

    bank = bank_account - parser.parse_value("91 $")
    books = books_account + parser.parse_value("40 $")
    cash = cash_account + parser.parse_value("51 $")
    tr2 = Transaction([bank, books, cash])

    bank2_account = parser.parse_account("Assets:Bank2")
    bank2_account.tags["foo"] = "bar"

    bank = bank2_account - parser.parse_value("33 $")
    books = books_account + parser.parse_value("33 $")
    tr3 = Transaction([bank, books])
    tr3.tags["baz"] = "hello world"
    books.tags["title"] = "Necronomicon"

    bank = bank_account - parser.parse_value("33 EUR")
    books = books_account + parser.parse_value("33 EUR")
    books.tags["foo"] = "bar"
    tr4 = Transaction([bank, books], date=date(2009, 12, 31))

    bank = bank_account - parser.parse_value("91 $")
    books = books_account + parser.parse_value("40 $")
    books.tags["date"] = date(2009, 3, 1)
    cash = cash_account + parser.parse_value("51 $")
    tr5 = Transaction([bank, books, cash], date=date(2010, 1, 1))

    return tr1, tr2, tr3, tr4, tr5

def test_filter(transactions):
    assert not three_entries(transactions[0],
                             transactions[0].entries[0])
    assert three_entries(transactions[1], transactions[1].entries[0])
    assert in_euro(transactions[0], transactions[0].entries[0])
    assert not in_euro(transactions[1], transactions[1].entries[0])

def test_filter_parse(parser, transactions):
    filter = Filter.parse(
        parser,
        lambda tr, entry: entry.account.name.startswith("Assets"))
    assert filter(transactions[0], transactions[0].entries[0])
    assert not filter(transactions[0], transactions[0].entries[1])

def test_filter_invert(transactions):
    assert (~three_entries)(transactions[0], transactions[0].entries[0])
    assert not (~three_entries)(transactions[1], transactions[1].entries[0])
    assert not (~in_euro)(transactions[0], transactions[0].entries[0])
    assert (~in_euro)(transactions[1], transactions[1].entries[0])

def test_filter_and(transactions):
    filter = three_entries & in_euro
    assert not filter(transactions[0], transactions[0].entries[0])
    assert not filter(transactions[1], transactions[1].entries[0])

def test_filter_or(transactions):
    filter = three_entries | in_euro
    assert filter(transactions[0], transactions[0].entries[0])
    assert filter(transactions[1], transactions[1].entries[0])

def test_has_account_filter(parser, transactions):
    filter = Filter.has_account(parser.parse_account("Assets:Bank"))
    assert filter(transactions[0], transactions[0].entries[0])
    assert not filter(transactions[0], transactions[0].entries[1])

def test_matches_filter(transactions):
    filter = Filter.matches(re.compile(r"ank"))
    assert filter(transactions[0], transactions[0].entries[0])
    assert not filter(transactions[0], transactions[0].entries[1])

def test_account_tag_filter(parser, transactions):
    filter = Account.tag_filter("foo", "bar")
    assert filter(transactions[2], transactions[2].entries[0])
    assert not filter(transactions[2], transactions[2].entries[1])

def test_account_tag_filter_empty(transactions):
    filter = Account.tag_filter("foo")
    assert filter(transactions[2], transactions[2].entries[0])
    assert not filter(transactions[2], transactions[2].entries[1])

def test_account_tag_filter_wrong(transactions):
    filter = Account.tag_filter("baz")
    assert not filter(transactions[2], transactions[2].entries[0])
    assert not filter(transactions[2], transactions[2].entries[1])

def test_transaction_tag_filter(transactions):
    filter = Transaction.tag_filter("baz", "hello world")
    assert filter(transactions[2], transactions[2].entries[0])
    assert filter(transactions[2], transactions[2].entries[1])
    assert filter(transactions[2], None)

def test_transaction_tag_filter_empty(transactions):
    filter = Transaction.tag_filter("baz", None)
    assert filter(transactions[2], transactions[2].entries[0])
    assert filter(transactions[2], transactions[2].entries[1])
    assert filter(transactions[2], None)

def test_transaction_tag_filter_wrong(transactions):
    filter = Transaction.tag_filter("foo", None)
    assert not filter(transactions[2], transactions[2].entries[0])
    assert not filter(transactions[2], transactions[2].entries[1])
    assert not filter(transactions[2], None)

def test_transaction_account_filter(transactions):
    filter = Transaction.account_tag_filter("foo", "bar")
    assert filter(transactions[2], None)

def test_entry_tag_filter(transactions):
    filter = Entry.tag_filter("title", "Necronomicon")
    assert filter(transactions[2], transactions[2].entries[1])
    assert not filter(transactions[2], transactions[2].entries[0])
    assert not filter(transactions[2], None)

def test_date_filter(parser):
    filter = DateFilter.parse(parser, "2010/10/01")
    assert filter.date == date(2010, 10, 1)

    with pytest.raises(ValueError):
        DateFilter.parse(parser, "foo")
    with pytest.raises(ValueError):
        DateFilter.parse(parser, "2011/15/12")

def test_begin_filter(parser, transactions):
    filter = BeginFilter.parse(parser, "2010")
    assert not filter(transactions[3], transactions[3].entries[0])
    assert filter(transactions[4], transactions[4].entries[0])
    assert not filter(transactions[4], transactions[4].entries[1])

def test_end_filter(parser, transactions):
    filter = EndFilter.parse(parser, "2010")
    assert filter(transactions[3], transactions[3].entries[0])
    assert not filter(transactions[4], transactions[4].entries[0])
    assert filter(transactions[4], transactions[4].entries[1])

def test_expression_filter(parser, transactions):
    filter = ExpressionFilter.parse(
        parser, "entry.account.name.startswith('Assets')")
    assert filter(transactions[3], transactions[3].entries[0])
    assert not filter(transactions[3], transactions[3].entries[1])

def testExpressionFilterDate(parser, transactions):
    filter = ExpressionFilter.parse(parser, "entry.date < date('2010')")
    assert filter(transactions[3], transactions[3].entries[0])
    assert not filter(transactions[4], transactions[4].entries[0])
    assert filter(transactions[4], transactions[4].entries[1])

def testExpressionFilterTag(parser, transactions):
    filter = ExpressionFilter.parse(parser, "entry.foo")
    assert not filter(transactions[3], transactions[3].entries[0])
    assert filter(transactions[3], transactions[3].entries[1])
