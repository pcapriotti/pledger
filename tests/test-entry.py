from pledger.entry import Entry
from pledger.account import Account
from pledger.value import Value

import unittest

class EntryTest(unittest.TestCase):
    def testParsing(self):
        value = Value.parse("34 EUR")
        account = Account.parse("Test Account")
        entry = Entry(account, value)
        self.assertEqual(entry, Entry.parse("  Test Account        34 EUR"))
