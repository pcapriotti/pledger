# Copyright (C) 2011 by Paolo Capriotti <p.capriotti@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pledger.entry import Entry
from pledger.parser import Parser
from pledger.value import Value
from datetime import date
from collections import namedtuple
import unittest

FakeTransaction = namedtuple("FakeTransaction", ["date"])

class EntryTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def testParsing(self):
        value = self.parser.parse_value("34 EUR")
        account = self.parser.parse_account("Test Account")
        entry = Entry(account, value)
        self.assertEqual(entry, self.parser.parse_entry("  Test Account        34 EUR"))

    def testEquality(self):
        value1 = self.parser.parse_value("34 EUR")
        value2 = self.parser.parse_value("12 $")
        account1 = self.parser.parse_account("Test")
        account2 = self.parser.parse_account("Bank")

        self.assertEqual(Entry(account1, value1), Entry(account1, value1))
        self.assertNotEqual(Entry(account1, value1), Entry(account2, value1))
        self.assertNotEqual(Entry(account1, value1), Entry(account1, value2))

    def testEntryParser(self):
        entry = self.parser.parse_entry("  Expenses:Books       61 EUR   ; :gift:")
        self.assertEqual("Expenses:Books", entry.account.name)
        self.assertEqual(Value.parse("61 EUR"), entry.amount)
        self.assertItemsEqual(["gift"], entry.tags.keys())

    def testEntryDict(self):
        entry = self.parser.parse_entry("  Expenses:Books       61 EUR   ; :gift:")
        entry2 = self.parser.parse_entry("  Expenses:Books       61 EUR")
        entry3 = self.parser.parse_entry("  Expenses:Books       51 EUR")
        entry4 = self.parser.parse_entry("    Expenses:Books       51 EUR")

        d = {}
        d[entry] = True
        d[entry2] = True
        d[entry3] = True
        d[entry4] = True

        self.assertItemsEqual([entry, entry2, entry3], d.keys())

    def testRepr(self):
        entry = self.parser.parse_entry("  Expenses:Books    55 EUR")
        s = str(entry)

        self.assertRegexpMatches(s, "Expenses:Books")
        self.assertRegexpMatches(s, "55.00 EUR")

    def testEntryDate(self):
        entry = self.parser.parse_entry("  Expenses:Books       61 EUR   ; [2011/03/03]")
        entry2 = self.parser.parse_entry("  Expenses:Books       61 EUR")
        transaction = FakeTransaction(date=date(2011, 03, 01))

        self.assertEqual(date(2011, 03, 03), entry.date(transaction))
        self.assertEqual(date(2011, 03, 01), entry2.date(transaction))

    def testEntryOfTransaction(self):
        transaction = FakeTransaction(date=date(2011, 03, 01))
        entry = self.parser.parse_entry("  Expenses:Books       61 EUR   ; [2011/03/03]").of(transaction)
        entry2 = self.parser.parse_entry("  Expenses:Books       61 EUR").of(transaction)

        self.assertEqual(date(2011, 03, 03), entry.date)
        self.assertEqual(date(2011, 03, 01), entry2.date)
