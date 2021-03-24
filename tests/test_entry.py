from pledger.entry import Entry
from pledger.parser import Parser
from pledger.value import Value
from datetime import date
from collections import namedtuple
import re

FakeTransaction = namedtuple("FakeTransaction", ["date"])

def test_parsing(parser):
    value = parser.parse_value("34 EUR")
    account = parser.parse_account("Test Account")
    entry = Entry(account, value)
    assert parser.parse_entry("  Test Account        34 EUR") == entry

def test_equality(parser):
    value1 = parser.parse_value("34 EUR")
    value2 = parser.parse_value("12 $")
    account1 = parser.parse_account("Test")
    account2 = parser.parse_account("Bank")

    assert Entry(account1, value1) == Entry(account1, value1)
    assert Entry(account1, value1) != Entry(account2, value1)
    assert Entry(account1, value1) != Entry(account1, value2)

def test_entry_parser(parser):
    entry = parser.parse_entry("  Expenses:Books       61 EUR   ; :gift:")
    assert entry.account.name == "Expenses:Books"
    assert entry.amount == Value.parse("61 EUR")
    assert list(entry.tags.keys()) == ["gift"]

def test_entry_dict(parser):
    entry = parser.parse_entry("  Expenses:Books       61 EUR   ; :gift:")
    entry2 = parser.parse_entry("  Expenses:Books       61 EUR")
    entry3 = parser.parse_entry("  Expenses:Books       51 EUR")
    entry4 = parser.parse_entry("    Expenses:Books       51 EUR")

    d = {}
    d[entry] = True
    d[entry2] = True
    d[entry3] = True
    d[entry4] = True

    assert set((entry, entry2, entry3)) == set(d.keys())

def test_repr(parser):
    entry = parser.parse_entry("  Expenses:Books    55 EUR")
    s = str(entry)

    assert re.search(r'Expenses:Books', s)
    assert re.search(r'55.00 EUR', s)

def test_entry_date(parser):
    entry = parser.parse_entry("  Expenses:Books       61 EUR   ; [2011/03/03]")
    entry2 = parser.parse_entry("  Expenses:Books       61 EUR")
    transaction = FakeTransaction(date=date(2011, 3, 1))

    assert entry.date(transaction) == date(2011, 3, 3)
    assert entry2.date(transaction) == date(2011, 3, 1)

def test_entry_of_transaction(parser):
    transaction = FakeTransaction(date=date(2011, 0o3, 0o1))
    entry = parser.parse_entry("  Expenses:Books       61 EUR   ; [2011/03/03]").of(transaction)
    entry2 = parser.parse_entry("  Expenses:Books       61 EUR").of(transaction)

    assert entry.date == date(2011, 3, 3)
    assert entry2.date == date(2011, 3, 1)
