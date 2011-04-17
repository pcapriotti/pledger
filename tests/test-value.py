import unittest
from decimal import Decimal
from pledger.value import Value, ZERO

class SingleCurrency(unittest.TestCase):
    def testSumNull(self):
        value = Value({ "EUR": Decimal(32) })
        self.assertEqual(value, value + ZERO)

    def testParsing(self):
        value = Value({ "EUR": Decimal("35.1") })
        self.assertEqual(value, Value.parse("35.1 EUR"))

if __name__ == '__main__':
    unittest.main()
