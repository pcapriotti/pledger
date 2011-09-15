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

import unittest
from pledger.transaction import Transaction, UnbalancedTransaction, UndefinedTransaction
from pledger.value import Value, ZERO
from pledger.entry import Entry
from pledger.parser import Parser, MalformedHeader

class TransactionTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.bank = self.parser.accounts["Assets"]["Bank"]
        self.expenses = self.parser.accounts["Expenses"]["Books"]

    def testParsing(self):
        str = "2011/04/15 * Bookshop\n" + \
              "    Assets:Bank       -40 EUR\n" + \
              "    Expenses:Books"
        value = self.parser.parse_value("40 EUR")
        entry1 = Entry(self.bank, -value)
        entry2 = Entry(self.expenses, value)
        tr = Transaction([entry1, entry2])
        self.assertEquals(tr, self.parser.parse_transaction(str))

    def testParsingComments(self):
        str = "; gift for wife\n" + \
              "2011/05/21 * Bookshop\n" + \
              "    Assets:Bank      -40 EUR\n" + \
              "    Expenses:Books"
        tr = self.parser.parse_transaction(str)

        value = self.parser.parse_value("40 EUR")
        self.assertEqual("Assets:Bank", tr.entries[0].account.name)
        self.assertEqual("Expenses:Books", tr.entries[1].account.name)
        self.assertEqual(-value, tr.entries[0].amount)
        self.assertEqual(value, tr.entries[1].amount)

    def testEmptyTransaction(self):
        str = ""
        self.assertIsNone(self.parser.parse_transaction(str))

        str = "; hello world"
        self.assertIsNone(self.parser.parse_transaction(str))

    def testParseUnbalanced(self):
        str = "2011/02/05 * Bookshop\n" + \
              "    Assets:Bank          -40 EUR\n" + \
              "    Expenses:Book        41 EUR"
        with self.assertRaises(UnbalancedTransaction) as cm:
            self.parser.parse_transaction(str)

    def testParseUndefined(self):
        str = "2011/02/05 * Bookshop\n" + \
              "    Assets:Bank\n" + \
              "    Expenses:Book"
        with self.assertRaises(UndefinedTransaction) as cm:
            self.parser.parse_transaction(str)

    def testMalformedHeader(self):
        str = "test 2011/02/05 * Bookshop\n" + \
              "    Assets:Bank          -40 EUR\n" + \
              "    Expenses:Book"
        with self.assertRaises(MalformedHeader) as cm:
            self.parser.parse_transaction(str)

    def testMalformedHeader2(self):
        str = " 2011/02/05 * Bookshop\n" + \
              "    Assets:Bank          -40 EUR\n" + \
              "    Expenses:Book"
        with self.assertRaises(MalformedHeader) as cm:
            self.parser.parse_transaction(str)

    def testUnbalanced(self):
        value = self.parser.parse_value("40 EUR")
        entry1 = Entry(self.bank, value)
        entry2 = Entry(self.expenses, value)
        self.assertRaises(UnbalancedTransaction, Transaction, [entry1, entry2])

    def testUndefined(self):
        entry1 = Entry(self.bank, None)
        entry2 = Entry(self.expenses, None)
        self.assertRaises(UndefinedTransaction, Transaction, [entry1, entry2])

    def testDefined(self):
        value = self.parser.parse_value("40 EUR")
        entry1 = Entry(self.bank, value)
        entry2 = Entry(self.expenses, None)
        tr = Transaction([entry1, entry2])
        self.assertEqual(-value, tr.entries[-1].amount)

    def testAmount(self):
        value = self.parser.parse_value("40 EUR")
        entry1 = Entry(self.bank, value)
        entry2 = Entry(self.expenses, None)
        tr = Transaction([entry1, entry2])
        self.assertEqual(ZERO, tr.amount)

    def testClone(self):
        value = self.parser.parse_value("40 EUR")
        entry1 = Entry(self.bank, value)
        entry2 = Entry(self.expenses, None)
        tr = Transaction([entry1, entry2])
        tr2 = tr.clone()
        self.assertFalse(id(tr) == id(tr2))
        self.assertItemsEqual(tr.entries, tr2.entries)
        self.assertEqual(tr.date, tr2.date)
        self.assertEqual(tr.label, tr2.label)
