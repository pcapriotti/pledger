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

class AccountTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.account = self.parser.parse_account("Assets:Bank")

    def testAccountAdd(self):
        amount = self.parser.parse_value("150 EUR")
        entry = self.account + amount
        self.assertEqual(self.account, entry.account)
        self.assertEqual(amount, entry.amount)

    def testAccountSub(self):
        amount = self.parser.parse_value("150 EUR")
        entry = self.account - amount
        self.assertEqual(self.account, entry.account)
        self.assertEqual(-amount, entry.amount)

    def testRoot(self):
        self.assertEqual(self.parser.accounts["Assets"], self.account.root())

    def testShortenedName(self):
        account = self.account["Joint:Savings:Yearly:Interest:Compound:Open"]
        size = 30
        name = account.shortened_name(size)

        self.assertLessEqual(len(name), size)
        self.assertEqual(7, len([x for x in name if x == ':']))

    def testSubName(self):
        account = self.account["Checking"]
        self.assertEqual('Bank:Checking', self.account.parent.sub_name(account))
        self.assertIsNone(self.account.sub_name(self.parser.accounts["Test"]))
