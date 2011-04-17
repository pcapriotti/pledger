import unittest
from pledger.account import Account
from pledger.transaction import Transaction
from pledger.value import Value
from pledger.entry import Entry

class TransactionTest(unittest.TestCase):
    def testParsing(self):
        str = "2011/04/15 * Bookshop\n" + \
              "    Assets:Bank       -40 EUR\n" + \
              "    Expenses:Books"
        bank = Account.parse("Assets:Bank")
        expenses = Account.parse("Expenses:Books")
        value = Value.parse("40 EUR")
        entry1 = Entry(bank, -value)
        entry2 = Entry(expenses, value)
        tr = Transaction([entry1, entry2])
        self.assertEquals(tr, Transaction.parse(str))
