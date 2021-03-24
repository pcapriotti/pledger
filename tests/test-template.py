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
from pledger.parser import Parser
from pledger.template import Template
from pledger.value import Value
from tests.fixtures import fixture_path


class FakeTemplate(Template):
    def generate(self, report):
        for record in report.generate():
            yield repr(record)


class FakeReport(Template):
    def __init__(self, records):
        self.records = records

    def generate(self):
        return iter(self.records)


class TemplateTest(unittest.TestCase):
    def setUp(self):
        self.template = FakeTemplate()
        self.parser = Parser()

    def testCall(self):
        lines = []
        report = FakeReport([1, 2, 3])
        self.template(report, lambda x: lines.append(x))
        self.assertEqual(["1", "2", "3"], lines)

    def testPad(self):
        text = self.template.pad("hello", 10)
        self.assertEqual("     hello", text)

    def testColoredPad(self):
        text = self.template.pad("hello", 10, 'red')
        self.assertRegex(text, "     .*hello.*")

    def testLPad(self):
        text = self.template.lpad("hello", 10)
        self.assertEqual("hello     ", text)

    def testColoredLPad(self):
        text = self.template.lpad("hello", 10, 'red')
        self.assertRegex(text, ".*hello.*     ")

    def testPrintValue(self):
        value = Value.parse("44 EUR")
        self.assertRegex(self.template.print_value(value), r'^ *44.00 EUR$')

    def testPrintNegativeValue(self):
        value = Value.parse("-44 EUR")
        self.assertRegex(self.template.print_value(value), r'^ *\S+-44.00 EUR\S+$')

    def testPrintNullValue(self):
        self.assertEqual("", self.template.print_value(None))

    def testPrintAccount(self):
        account = self.parser.accounts["Assets:Bank:Checking:Joint"]
        text = self.template.print_account(account, None)
        self.assertRegex(text, "Assets:Bank:Checking:Joint")

    def testPrintAccountShortened(self):
        account = self.parser.accounts["Assets:Bank:Checking:Joint"]
        text = self.template.print_account(account, 20)
        self.assertRegex(text, ".*:.*:.*:Joint")
        self.assertLessEqual(len(list(filter(str.isalpha, text))), 20)

    def testPrintLabel(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        transaction = ledger.transactions[1]
        self.assertEqual("Bookshop", transaction.label)
        text = self.template.print_label(transaction, 30)
        self.assertRegex(text, r' *\S+Bookshop')

    def testPrintClearedLabel(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        transaction = ledger.transactions[1]
        transaction.tags["cleared"] = True
        self.assertEqual("Bookshop", transaction.label)
        text = self.template.print_label(transaction, 30)
        self.assertRegex(text, r' *Bookshop')
