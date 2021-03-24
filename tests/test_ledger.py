import unittest
from pledger.parser import Parser
from tests.fixtures import fixture_path


class TestLedger(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def testFilename(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        self.assertEqual(fixture_path("test.dat"), ledger.absolute_filename("test.dat"))
