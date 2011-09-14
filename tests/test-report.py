import unittest
from tests.fixtures import fixture_path
from pledger.filter import Filter
from pledger.parser import Parser
from pledger.report import reports, ReportRegistry
from pledger.rule import RuleCollection
from pledger.sorting import Sorting, MapSorting
from pledger.value import Value, ZERO

class RegisterReportTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.report_factory = reports.get("register")

    def testSimpleReport(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        sorting = MapSorting(lambda x: x.date)
        report = self.report_factory(ledger, RuleCollection(), [], Filter.null, sorting)
        records = list(report.generate())

        self.assertEqual(4, len(records))
        self.assertEqual(
            [(u'Assets:Bank', Value.parse('1500 EUR')),
             (u'Equity:Capital', Value.parse('-1500 EUR')),
             (u'Expenses:Books', Value.parse('35 EUR')),
             (u'Assets:Bank', Value.parse('-35 EUR'))],
            [(record.entry.account.name, record.entry.amount) for record in records])


    def testReportOrdering(self):
        ledger = self.parser.parse_ledger(fixture_path("sorting.dat"))
        sorting = MapSorting(lambda x: x.date)
        report = self.report_factory(ledger, RuleCollection(), [], Filter.null, sorting)

        self.assertEqual(
            [unicode(chr(i)) for i in xrange(ord('A'), ord('N') + 1) for _ in xrange(2)],
            [record.transaction.label for record in report.generate()])

    def testEmptyRegister(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        sorting = MapSorting(lambda x: x.date)
        filter = self.parser.accounts["Expenses"]["Clothing"].filter()
        report = self.report_factory(ledger, RuleCollection(), [], filter, sorting)
        records = list(report.generate())

        self.assertEqual(0, len(records))

class BalanceReportTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.report_factory = reports.get("balance")

    def testSimpleReport(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        sorting = Sorting(lambda x: x)
        report = self.report_factory(ledger, RuleCollection(), [], Filter.null, sorting)

        self.assertEqual(
            [(u'Assets:Bank', Value.parse("1465 EUR")),
             (u'Equity:Capital', Value.parse("-1500 EUR")),
             (u'Expenses:Books', Value.parse("35 EUR"))],
            [(record.account, record.amount) for record in report.generate() if record.account])

    def testEmptyBalance(self):
        ledger = self.parser.parse_ledger("<test>", "")
        sorting = Sorting(lambda x: x)
        report = self.report_factory(ledger, RuleCollection(), [], Filter.null, sorting)
        records = list(report.generate())

        self.assertEqual(1, len(records))
        self.assertIsNone(records[0].level)

class ReportRegistryTest(unittest.TestCase):
    def setUp(self):
        self.registry = ReportRegistry({})

    def testGet(self):
        self.registry.add('register', 'register factory')
        self.registry.add('balance', 'balance factory')
        self.assertEqual('register factory', self.registry['register'])
        self.assertEqual('register factory', self.registry.get('reg'))

    def testAddMultiple(self):
        self.registry.add('register', 'register factory')
        self.assertRaises(Exception, self.registry.add, 'register', 'register factory 2')

    def testAmbiguous(self):
        self.registry.add('register', 'register factory')
        self.registry.add('reimbursements', 'reimbursement factory')

        self.assertIsNone(self.registry.get('re'))
