import unittest
from decimal import Decimal, InvalidOperation
from pledger.value import Value, ZERO

class SingleCurrency(unittest.TestCase):
    def testSumNull(self):
        value = Value({ "EUR": Decimal(32) })
        self.assertEqual(value, value + ZERO)

    def testParsing(self):
        value = Value({ "EUR": Decimal("35.1") })
        self.assertEqual(value, Value.parse("35.1 EUR"))

    def testParseNoCurrency(self):
        self.assertRaises(InvalidOperation, Value.parse("35.1"))

    def testParseInvalidDecimal(self):
        self.assertRaises(ValueError, Value.parse("12.1.1 EUR"))

    def testCurrencies(self):
        value = Value({ "EUR": Decimal("21.36") })
        self.assertEqual(["EUR"], list(value.currencies()))

    def testComponents(self):
        value = Value({ "EUR": Decimal("31.99") })
        self.assertEqual([value], list(value.components()))
        self.assertEqual([value], list(value.components(["EUR"])))
        self.assertEqual([ZERO], list(value.components(["USD"])))
        self.assertEqual([ZERO], list(value.components([])))

    def testNeg(self):
        amount = Decimal("21.36")
        value = Value({ "EUR": amount })
        self.assertEqual(Value({ "EUR": -amount }), -value)

    def testNegative(self):
        value = Value({ "EUR": Decimal("31.99") })
        self.assertFalse(value.negative())
        self.assertTrue((-value).negative())

    def testEquality(self):
        value = Value({ "EUR": Decimal("31.99") })
        value2 = Value({ "EUR": Decimal("31.99") })
        value3 = Value({ "EUR": Decimal("31.98") })
        self.assertTrue(value == value2)
        self.assertFalse(value == value3)
        self.assertFalse(value == None)

    def testMultiplication(self):
        value = Value({ "EUR": Decimal("31.99") })
        value2 = Value({ "EUR": Decimal("63.98") })
        self.assertEqual(value2, value * Decimal(2))
        self.assertEqual(value2, value * Decimal("2.00001"))

    def testFormat(self):
        value = Value({ "EUR": Decimal("31.992371") })
        self.assertEqual("31.99 EUR", str(value))

    def testComparison(self):
        value = Value({ "EUR": Decimal("31.99") })
        value2 = Value({ "EUR": Decimal("21.36") })
        self.assertGreater(value, value2)
        self.assertLess(value2, value)
        self.assertGreaterEqual(value, value2)
        self.assertGreaterEqual(value, value)
        self.assertLessEqual(value2, value)
        self.assertLessEqual(value2, value2)

class MultipleCurrencies(unittest.TestCase):
    def testComponents(self):
        value1 = Value({ "EUR" : Decimal("81.45") })
        value2 = Value({ "USD" : Decimal("-12.44") })
        value = Value({"EUR" : Decimal("81.45"),
                       "USD" : Decimal("-12.44") })
        self.assertItemsEqual([value1, value2], value.components())

if __name__ == '__main__':
    unittest.main()
