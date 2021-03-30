from pledger.account import Account
from pledger.filter import Filter
from pledger.parser import Parser
from pledger.report import reports, ReportRegistry
from pledger.rule import RuleCollection
from pledger.sorting import Sorting, MapSorting
from pledger.value import Value, ZERO
import pytest


@pytest.fixture
def registry():
    return ReportRegistry({})


def test_simple_report(parser, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    sorting = MapSorting(lambda x: x.date)
    report = reports.get("register")(parser,
                                     RuleCollection(),
                                     Filter.null,
                                     sorting)
    records = list(report.generate([ledger]))

    assert len(records) == 4
    assert [(record.entry.account.name,
             record.entry.amount,
             record.total) for record in records] == \
        [('Assets:Bank', Value.parse('1500 EUR'), Value.parse('1500 EUR')),
         ('Equity:Capital', Value.parse('-1500 EUR'), ZERO),
         ('Expenses:Books', Value.parse('35 EUR'), Value.parse('35 EUR')),
         ('Assets:Bank', Value.parse('-35 EUR'), ZERO)]


def test_report_ordering(parser, data_file):
    ledger = parser.parse_ledger(data_file("sorting.dat"))
    sorting = MapSorting(lambda x: x.date)
    report = reports.get("register")(parser,
                                     RuleCollection(),
                                     Filter.null,
                                     sorting)

    assert [record.transaction.label for record in report.generate([ledger])] == \
        [str(chr(i)) for i in range(ord('A'), ord('N') + 1) for _ in range(2)]


def test_empty_register(parser, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    sorting = MapSorting(lambda x: x.date)
    filter = parser.parse_account("Expenses:Clothing").filter()
    report = reports.get("register")(parser, RuleCollection(), filter, sorting)
    records = list(report.generate([ledger]))

    assert len(records) == 0


def test_simple_report(parser, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    sorting = Sorting(lambda x: x)
    report = reports.get("balance")(parser,
                                    RuleCollection(),
                                    Filter.null,
                                    sorting)

    assert [(record.account, record.amount)
            for record in report.generate([ledger])
            if record.account] == \
        [('Assets:Bank', Value.parse("1465 EUR")),
         ('Equity:Capital', Value.parse("-1500 EUR")),
         ('Expenses:Books', Value.parse("35 EUR"))]


def test_empty_balance(parser):
    ledger = parser.parse_ledger("<test>", "")
    sorting = Sorting(lambda x: x)
    report = reports.get("balance")(parser,
                                    RuleCollection(),
                                    Filter.null,
                                    sorting)
    records = list(report.generate([ledger]))

    assert len(records) == 1
    assert records[0].level is None


def test_get(registry):
    registry.add('register', 'register factory')
    registry.add('balance', 'balance factory')
    assert registry['register'] == 'register factory'
    assert registry.get('reg') == 'register factory'


def test_add_multiple(registry):
    registry.add('register', 'register factory')
    with pytest.raises(Exception):
        registry.add('register', 'register factory 2')


def testAmbiguous(registry):
    registry.add('register', 'register factory')
    registry.add('reimbursements', 'reimbursement factory')

    assert registry.get('re') is None
