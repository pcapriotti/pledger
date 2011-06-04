from pledger.entry import Entry
from pledger.parser import Parser

import unittest

class EntryTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def testParsing(self):
        value = self.parser.parse_value("34 EUR")
        account = self.parser.parse_account("Test Account")
        entry = Entry(account, value)
        self.assertEqual(entry, self.parser.parse_entry("  Test Account        34 EUR"))
