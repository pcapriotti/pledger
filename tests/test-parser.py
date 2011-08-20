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
from tests.fixtures import fixture_path
from datetime import date

class ParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def testSimpleLedger(self):
        ledger = self.parser.parse_ledger(fixture_path("simple.dat"))
        self.assertEqual(2, len(ledger.transactions))

    def testLedgerWithTags(self):
        ledger = self.parser.parse_ledger(fixture_path("tags.dat"))
        self.assertEqual(2, len(ledger.transactions))
        tr1 = ledger.transactions[0]
        self.assertIsNotNone(tr1.tags["balance"])
        self.assertEqual(date(2011, 1, 1), tr1.entries[1].date(tr1))
        tr2 = ledger.transactions[1]
        self.assertEqual("Dracula", tr2.entries[0].tags["title"])

    def testTags(self):
        self.assertEqual({ "foo":"bar" }, self.parser.parse_tags("; foo:bar \t "))
        self.assertEqual({ "foo":"1", "bar":"2", "baz":"" },
                self.parser.parse_tags("; :baz: foo:1 \tbar:2"))

    def testTagsWithSpaces(self):
        self.assertEqual({ "foo":"hello world" },
                self.parser.parse_tags('; foo:"hello world"'))
        self.assertEqual({ "foo":'hello "world"' },
                self.parser.parse_tags('; foo:\'hello "world"\''))
        self.assertEqual({ "foo":"hello world", "bar":"0", "baz":"5" },
                self.parser.parse_tags(';bar:0 foo:"hello world" baz:5'))
