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
import re
from datetime import date
from pledger.account import Account
from pledger.entry import Entry
from pledger.filter import *
from pledger.parser import Parser
from pledger.transaction import Transaction

class TestFilter(unittest.TestCase):
    def setUp(self):
        self.three_entries = Filter(lambda tr, entry: len(tr.entries) == 3)
        self.in_euro = Filter(lambda tr, entry: list(entry.amount.currencies()) == ["EUR"])

        self.parser = Parser()
        bank_account = self.parser.parse_account("Assets:Bank")
        books_account = self.parser.parse_account("Expenses:Books")
        cash_account = self.parser.parse_account("Assets:Cash")

        bank = bank_account - self.parser.parse_value("33 EUR")
        books = books_account + self.parser.parse_value("33 EUR")
        self.tr1 = Transaction([bank, books])

        bank = bank_account - self.parser.parse_value("91 $")
        books = books_account + self.parser.parse_value("40 $")
        cash = cash_account + self.parser.parse_value("51 $")
        self.tr2 = Transaction([bank, books, cash])
        
    def testFilter(self):
        self.assertFalse(self.three_entries(self.tr1, self.tr1.entries[0]))
        self.assertTrue(self.three_entries(self.tr2, self.tr2.entries[0]))
        self.assertTrue(self.in_euro(self.tr1, self.tr1.entries[0]))
        self.assertFalse(self.in_euro(self.tr2, self.tr2.entries[0]))

    def testFilterParse(self):
        filter = Filter.parse(self.parser, lambda tr, entry: entry.account.name.startswith("Assets"))
        self.assertTrue(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertFalse(list(filter(self.tr1, self.tr1.entries[1])))

    def testFilterInvert(self):
        self.assertTrue((~self.three_entries)(self.tr1, self.tr1.entries[0]))
        self.assertFalse((~self.three_entries)(self.tr2, self.tr2.entries[0]))
        self.assertFalse((~self.in_euro)(self.tr1, self.tr1.entries[0]))
        self.assertTrue((~self.in_euro)(self.tr2, self.tr2.entries[0]))

    def testFilterAnd(self):
        filter = self.three_entries & self.in_euro
        self.assertFalse(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertFalse(list(filter(self.tr2, self.tr2.entries[0])))

    def testFilterOr(self):
        filter = self.three_entries | self.in_euro
        self.assertTrue(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertTrue(list(filter(self.tr2, self.tr2.entries[0])))

    def testHasAccountFilter(self):
        filter = Filter.has_account(self.parser.parse_account("Assets:Bank"))
        self.assertTrue(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertFalse(list(filter(self.tr1, self.tr1.entries[1])))

    def testMatchesFilter(self):
        filter = Filter.matches(re.compile(r"ank"))
        self.assertTrue(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertFalse(list(filter(self.tr1, self.tr1.entries[1])))

class TestTagFilters(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        bank_account = self.parser.parse_account("Assets:Bank")
        books_account = self.parser.parse_account("Expenses:Books")
        bank_account.tags["foo"] = "bar"

        self.bank = bank_account - self.parser.parse_value("33 $")
        self.books = books_account + self.parser.parse_value("33 $")
        self.tr = Transaction([self.bank, self.books])
        self.tr.tags["baz"] = "hello world"
        self.books.tags["title"] = "Necronomicon"

    def testAccountTagFilter(self):
        filter = Account.tag_filter("foo", "bar")
        self.assertTrue(list(filter(self.tr, self.bank)))
        self.assertFalse(list(filter(self.tr, self.books)))

    def testAccountTagFilterEmpty(self):
        filter = Account.tag_filter("foo")
        self.assertTrue(list(filter(self.tr, self.bank)))
        self.assertFalse(list(filter(self.tr, self.books)))

    def testAccountTagFilterWrong(self):
        filter = Account.tag_filter("baz")
        self.assertFalse(list(filter(self.tr, self.bank)))
        self.assertFalse(list(filter(self.tr, self.books)))

    def testTransactionTagFilter(self):
        filter = Transaction.tag_filter("baz", "hello world")
        self.assertTrue(list(filter(self.tr, self.bank)))
        self.assertTrue(list(filter(self.tr, self.books)))
        self.assertTrue(list(filter(self.tr, None)))

    def testTransactionTagFilterEmpty(self):
        filter = Transaction.tag_filter("baz", None)
        self.assertTrue(list(filter(self.tr, self.bank)))
        self.assertTrue(list(filter(self.tr, self.books)))
        self.assertTrue(list(filter(self.tr, None)))

    def testTransactionTagFilterWrong(self):
        filter = Transaction.tag_filter("foo", None)
        self.assertFalse(list(filter(self.tr, self.bank)))
        self.assertFalse(list(filter(self.tr, self.books)))
        self.assertFalse(list(filter(self.tr, None)))

    def testTransactionAccountFilter(self):
        filter = Transaction.account_tag_filter("foo", "bar")
        self.assertTrue(list(filter(self.tr, None)))

    def testEntryTagFilter(self):
        filter = Entry.tag_filter("title", "Necronomicon")
        self.assertTrue(list(filter(self.tr, self.books)))
        self.assertFalse(list(filter(self.tr, self.bank)))
        self.assertFalse(list(filter(self.tr, None)))

class TestCLIFilters(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        bank_account = self.parser.parse_account("Assets:Bank")
        books_account = self.parser.parse_account("Expenses:Books")
        cash_account = self.parser.parse_account("Assets:Cash")

        bank = bank_account - self.parser.parse_value("33 EUR")
        books = books_account + self.parser.parse_value("33 EUR")
        books.tags["foo"] = "bar"
        self.tr1 = Transaction([bank, books], date=date(2009, 12, 31))

        bank = bank_account - self.parser.parse_value("91 $")
        books = books_account + self.parser.parse_value("40 $")
        books.tags["date"] = date(2009, 3, 1)
        cash = cash_account + self.parser.parse_value("51 $")
        self.tr2 = Transaction([bank, books, cash], date=date(2010, 1, 1))

    def testDateFilter(self):
        filter = DateFilter.parse(self.parser, "2010/10/01")
        self.assertEqual(date(2010, 10, 1), filter.date)

        self.assertRaises(ValueError, DateFilter.parse, self.parser, "foo")
        self.assertRaises(ValueError, DateFilter.parse, self.parser, "2011/15/12")

    def testBeginFilter(self):
        filter = BeginFilter.parse(self.parser, "2010")
        self.assertFalse(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertTrue(list(filter(self.tr2, self.tr2.entries[0])))
        self.assertFalse(list(filter(self.tr2, self.tr2.entries[1])))

    def testEndFilter(self):
        filter = EndFilter.parse(self.parser, "2010")
        self.assertTrue(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertFalse(list(filter(self.tr2, self.tr2.entries[0])))
        self.assertTrue(list(filter(self.tr2, self.tr2.entries[1])))

    def testExpressionFilter(self):
        filter = ExpressionFilter.parse(self.parser, "entry.account.name.startswith('Assets')")
        self.assertTrue(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertFalse(list(filter(self.tr1, self.tr1.entries[1])))

    def testExpressionFilterDate(self):
        filter = ExpressionFilter.parse(self.parser, "entry.date < date('2010')")
        self.assertTrue(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertFalse(list(filter(self.tr2, self.tr2.entries[0])))
        self.assertTrue(list(filter(self.tr2, self.tr2.entries[1])))

    def testExpressionFilterTag(self):
        filter = ExpressionFilter.parse(self.parser, "entry.foo")
        self.assertFalse(list(filter(self.tr1, self.tr1.entries[0])))
        self.assertTrue(list(filter(self.tr1, self.tr1.entries[1])))
