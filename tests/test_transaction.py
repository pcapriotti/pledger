from pledger.transaction import Transaction, UnbalancedTransaction, UndefinedTransaction
from pledger.value import Value, ZERO
from pledger.entry import Entry
from pledger.parser import Parser, MalformedHeader
import pytest
import re


@pytest.fixture
def bank(parser):
    return parser.parse_account("Assets:Bank")

@pytest.fixture
def expenses(parser):
    return parser.parse_account("Expenses:Books")

def test_parsing(parser, bank, expenses):
    str = "2011/04/15 * Bookshop\n" + \
          "    Assets:Bank       -40 EUR\n" + \
          "    Expenses:Books"
    value = parser.parse_value("40 EUR")
    entry1 = Entry(bank, -value)
    entry2 = Entry(expenses, value)
    tr = Transaction([entry1, entry2])
    assert parser.parse_transaction(str) == tr

def test_parsing_comments(parser):
    str = "; gift for wife\n" + \
          "2011/05/21 * Bookshop\n" + \
          "    Assets:Bank      -40 EUR\n" + \
          "    Expenses:Books"
    tr = parser.parse_transaction(str)

    value = parser.parse_value("40 EUR")
    assert tr.entries[0].account.name == "Assets:Bank"
    assert tr.entries[1].account.name == "Expenses:Books"
    assert tr.entries[0].amount == -value
    assert tr.entries[1].amount == value

def test_empty_transaction(parser):
    str = ""
    assert parser.parse_transaction(str) is None

    str = "; hello world"
    assert parser.parse_transaction(str) is None

def test_parse_unbalanced(parser):
    str = "2011/02/05 * Bookshop\n" + \
          "    Assets:Bank          -40 EUR\n" + \
          "    Expenses:Book        41 EUR"
    with pytest.raises(UnbalancedTransaction):
        parser.parse_transaction(str)

def test_parse_undefined(parser):
    str = "2011/02/05 * Bookshop\n" + \
          "    Assets:Bank\n" + \
          "    Expenses:Book"
    with pytest.raises(UndefinedTransaction):
        parser.parse_transaction(str)

def test_malformed_header(parser):
    str = "test 2011/02/05 * Bookshop\n" + \
          "    Assets:Bank          -40 EUR\n" + \
          "    Expenses:Book"
    with pytest.raises(MalformedHeader):
        parser.parse_transaction(str)

def test_malformed_header2(parser):
    str = " 2011/02/05 * Bookshop\n" + \
          "    Assets:Bank          -40 EUR\n" + \
          "    Expenses:Book"
    with pytest.raises(MalformedHeader):
        parser.parse_transaction(str)

def test_unbalanced(parser, bank, expenses):
    value = parser.parse_value("40 EUR")
    entry1 = Entry(bank, value)
    entry2 = Entry(expenses, value)
    with pytest.raises(UnbalancedTransaction):
        Transaction([entry1, entry2])

def test_undefined(bank, expenses):
    entry1 = Entry(bank, None)
    entry2 = Entry(expenses, None)
    with pytest.raises(UndefinedTransaction):
        Transaction([entry1, entry2])

def test_defined(parser, bank, expenses):
    value = parser.parse_value("40 EUR")
    entry1 = Entry(bank, value)
    entry2 = Entry(expenses, None)
    tr = Transaction([entry1, entry2])
    assert tr.entries[-1].amount == -value

def test_repr(parser):
    value = parser.parse_value("50 EUR")
    entry1 = Entry(bank, value)
    entry2 = Entry(expenses, None)
    tr = Transaction([entry1, entry2])
    assert re.search("Transaction", repr(tr))

def test_transaction_entries(parser, bank, expenses):
    value = parser.parse_value("50 EUR")
    entry1 = Entry(bank, value)
    entry2 = Entry(expenses, None)
    tr = Transaction([entry1, entry2])
    assert tr[0] == entry1
    assert tr[1] == entry2

def test_amount(parser, bank, expenses):
    value = parser.parse_value("40 EUR")
    entry1 = Entry(bank, value)
    entry2 = Entry(expenses, None)
    tr = Transaction([entry1, entry2])
    assert tr.amount == ZERO

def test_clone(parser, bank, expenses):
    value = parser.parse_value("40 EUR")
    entry1 = Entry(bank, value)
    entry2 = Entry(expenses, None)
    tr = Transaction([entry1, entry2])
    tr2 = tr.clone()
    assert id(tr) != id(tr2)
    assert tr.entries == tr2.entries
    assert tr.date == tr2.date
    assert tr.label == tr2.label
