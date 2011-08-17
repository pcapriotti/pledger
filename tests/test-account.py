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

