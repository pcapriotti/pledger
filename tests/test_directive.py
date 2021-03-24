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
from pledger.directive import *
from pledger.ledger_processor import LedgerProcessor


class ProcessorStub(object):
    def __init__(self, root):
        self.account = root
        self.included  = []

    def add_account_prefix(self, prefix):
        self.account = self.account[prefix]

    def remove_account_prefix(self):
        self.account = self.account.parent

    def include(self, filename):
        self.included.append(filename)


class DirectiveTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.processor = ProcessorStub(self.parser.accounts)

    def testDirectiveRegistry(self):
        self.assertEqual(AccountDirective, Directive.directives['account'])
        self.assertIsNone(Directive.directives.get('non-existing-directive'))

    def testUnsupportedDirective(self):
        with self.assertRaises(UnsupportedDirective) as cm:
            self.parser.parse_directive("!nonexisting")

        self.assertRegex(str(cm.exception), "nonexisting")

    def testAccountDirective(self):
        directive = AccountDirective("Assets")
        self.assertIsNone(self.processor.account.name)
        directive.execute(self.processor)
        self.assertEqual("Assets", self.processor.account.name)

    def testEndAccountDirective(self):
        directive = EndAccountDirective()
        self.processor.add_account_prefix("Assets")
        directive.execute(self.processor)
        self.assertIsNone(self.processor.account.name)

    def testIncludeDirective(self):
        directive = IncludeDirective("test.dat")
        self.assertEqual([], self.processor.included)
        directive.execute(self.processor)
        self.assertEqual(["test.dat"], self.processor.included)

    def testDirectiveParsing(self):
        directive = self.parser.parse_directive("!include test.dat")
        self.assertEqual("test.dat", directive.filename)
