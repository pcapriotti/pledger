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
