import unittest
from pledger.transaction import Transaction, UnbalancedTransaction, UndefinedTransaction
from pledger.value import Value, ZERO
from pledger.entry import Entry
from pledger.parser import Parser

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
