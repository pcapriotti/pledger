from pledger.parser import Parser
from pledger.template import Template
from pledger.value import Value
import pytest
import re


class FakeTemplate(Template):
    def generate(self, ledgers, report):
        for record in report.generate(ledgers):
            yield repr(record)


class FakeReport(Template):
    def __init__(self, records):
        self.records = records

    def generate(self, ledgers):
        return iter(self.records)


@pytest.fixture
def template():
    return FakeTemplate()


def test_call(template):
    lines = []
    report = FakeReport([1, 2, 3])
    template([], report, lambda x: lines.append(x))
    assert lines == ["1", "2", "3"]


def test_pad(template):
    text = template.pad("hello", 10)
    assert text == "     hello"


def test_colored_pad(template):
    text = template.pad("hello", 10, "red")
    assert re.search("     .*hello.*", text)


def test_lpad(template):
    text = template.lpad("hello", 10)
    assert text == "hello     "


def test_colored_lpad(template):
    text = template.lpad("hello", 10, "red")
    assert re.search(".*hello.*     ", text)


def test_print_value(template):
    value = Value.parse("44 EUR")
    assert re.match(r" *44\.00 EUR$", template.print_value(value))


def test_print_negative_value(template):
    value = Value.parse("-44 EUR")
    assert re.match(r" *\S+-44.00 EUR\S+$", template.print_value(value))


def test_print_null_value(template):
    assert template.print_value(None) == ""


def test_print_account(parser, template):
    account = parser.parse_account("Assets:Bank:Checking:Joint")
    text = template.print_account(account, None)
    assert re.search("Assets:Bank:Checking:Joint", text)


def test_print_account_shortened(parser, template):
    account = parser.parse_account("Assets:Bank:Checking:Joint")
    text = template.print_account(account, 20)
    assert re.search(".*:.*:.*:Joint", text)
    assert len(list(filter(str.isalpha, text))) <= 20


def test_print_label(parser, template, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    transaction = ledger.transactions[1]
    assert transaction.label == "Bookshop"
    text = template.print_label(transaction, 30)
    assert re.search(r" *\S+Bookshop", text)


def test_print_cleared_label(parser, template, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    transaction = ledger.transactions[1]
    transaction.tags["cleared"] = True
    assert transaction.label == "Bookshop"
    text = template.print_label(transaction, 30)
    assert re.search(r" *Bookshop", text)
