import unittest
from tests.fixtures import fixture_path
from pledger.filter import Filter
from pledger.parser import Parser
from pledger.report import reports
from pledger.rule import RuleCollection
from pledger.sorting import MapSorting

class RegisterReportTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.report_factory = reports.get("register")

    def testReportOrdering(self):
        ledger = self.parser.parse_ledger(fixture_path("sorting.dat"))
        sorting = MapSorting(lambda x: x.date)
        report = self.report_factory(ledger, RuleCollection(), [], Filter.null, sorting)

        self.assertEqual(
            [unicode(chr(i)) for i in xrange(ord('A'), ord('N') + 1) for _ in xrange(2)],
            [record.transaction.label for record in report.generate()])
