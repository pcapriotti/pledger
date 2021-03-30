from pledger.entry import Entry
from pledger.ledger_processor import LedgerProcessor
from pledger.parser import Parser
from pledger.value import Value


class TransactionCollector(object):
    def __init__(self):
        self.transactions = []

    def on_transaction(self, transaction, entries):
        self.transactions.append(transaction)


def test_account_prefix(parser, rules, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    processor = LedgerProcessor(parser, rules)
    collector = TransactionCollector()
    processor.add_listener(collector)

    processor.add_account_prefix("Business")
    processor.run(ledger)

    for transaction in collector.transactions:
        for entry in transaction.entries:
            assert entry.account.path.components[0] == "Business"


def test_remove_account_prefix(parser, rules, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    processor = LedgerProcessor(parser, rules)
    collector = TransactionCollector()
    processor.add_listener(collector)

    assert len(ledger.transactions) == 2

    processor.add_account_prefix("Business")
    ledger.transactions[0].execute(processor)

    for transaction in collector.transactions:
        for entry in transaction.entries:
            assert entry.account.path.components[0] == "Business"

    collector.transactions = []
    processor.remove_account_prefix()

    ledger.transactions[0].execute(processor)

    for transaction in collector.transactions:
        for entry in transaction.entries:
            assert entry.account.path.components[0] != "Business"


def test_include(parser, rules, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    processor = LedgerProcessor(parser, rules)
    collector = TransactionCollector()
    processor.add_listener(collector)

    processor.run(ledger)
    processor.include("extra.dat")

    assert len(collector.transactions) == 3


def test_multiple(parser, rules, data_file):
    processor = LedgerProcessor(parser, rules)
    collector = TransactionCollector()
    processor.add_listener(collector)

    processor.run(parser.parse_ledger(data_file("simple.dat")))
    processor.run(parser.parse_ledger(data_file("extra.dat")))

    assert len(collector.transactions) == 3

def test_compact(parser, rules, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    processor = LedgerProcessor(parser, rules)
    entry = ledger.transactions[1].entries[0]
    assert entry.amount == Value.parse("35 EUR")
    # add entry
    entry2 = Entry(entry.account, Value.parse("-5 EUR"))
    ledger.transactions[1].entries.append(entry2)
    # rebalance transaction
    ledger.transactions[1].entries[1].amount += Value.parse("5 EUR")

    collector = TransactionCollector()
    processor.add_listener(collector)
    processor.run(ledger)

    assert len(collector.transactions) == 2
    assert len(collector.transactions[1].entries) == 2
    assert collector.transactions[1][0].amount == Value.parse("30 EUR")


def test_parse_account_root(parser, rules, data_file):
    ledger = parser.parse_ledger(data_file("root.dat"))
    processor = LedgerProcessor(parser, rules)
    collector = TransactionCollector()
    processor.add_listener(collector)
    processor.run(ledger)

    assert len(collector.transactions) == 1

    tr = collector.transactions[0]
    assert tr[0].account.name == "Personal:Assets:Bank"
    assert tr[1].account.name == "Business:Expenses:Salary"
