from pledger.util import PledgerException
from pledger.transaction import Transaction
from datetime import date
import pytest


def test_simple_ledger(parser, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    assert len(ledger.transactions) == 2


def test_ledger_with_tags(parser, data_file):
    ledger = parser.parse_ledger(data_file("tags.dat"))
    assert len(ledger.transactions) == 2
    tr1 = ledger.transactions[0]
    assert tr1.tags["balance"] is not None
    assert tr1.entries[1].date(tr1) == date(2011, 1, 1)
    tr2 = ledger.transactions[1]
    assert tr2.entries[0].tags["title"] == "Dracula"


def test_tags(parser):
    assert parser.parse_tags("; foo:bar \t ") == {"foo": "bar"}
    assert parser.parse_tags("; :baz: foo:1 \tbar:2") == {
        "foo": "1",
        "bar": "2",
        "baz": "",
    }


def test_tags_with_spaces(parser):
    assert parser.parse_tags('; foo:"hello world"') == {"foo": "hello world"}
    assert parser.parse_tags("; foo:'hello \"world\"'") == {"foo": 'hello "world"'}
    assert parser.parse_tags(';bar:0 foo:"hello world" baz:5') == {
        "foo": "hello world",
        "bar": "0",
        "baz": "5",
    }


def test_parse_error(parser, data_file):
    with pytest.raises(PledgerException) as e:
        parser.parse_ledger(data_file("errors.dat"))

    assert e.value.line_number == 2
    assert e.value.filename == data_file("errors.dat")
