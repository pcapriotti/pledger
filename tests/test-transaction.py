import unittest
from pledger.transaction import Transaction
from pledger.value import Value
from pledger.entry import Entry
from pledger.parser import Parser

class TransactionTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def testParsing(self):
        str = "2011/04/15 * Bookshop\n" + \
              "    Assets:Bank       -40 EUR\n" + \
              "    Expenses:Books"
        bank = self.parser.parse_account("Assets:Bank")
        expenses = self.parser.parse_account("Expenses:Books")
        value = self.parser.parse_value("40 EUR")
        entry1 = Entry(bank, -value)
        entry2 = Entry(expenses, value)
        tr = Transaction([entry1, entry2])
        self.assertEquals(tr, self.parser.parse_transaction(str))
