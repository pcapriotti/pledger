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
        self.assertEqual("0", str(ZERO))

    def testComparison(self):
        value = Value({ "EUR": Decimal("31.99") })
        value2 = Value({ "EUR": Decimal("21.36") })
        self.assertGreater(value, value2)
        self.assertLess(value2, value)
        self.assertGreaterEqual(value, value2)
        self.assertGreaterEqual(value, value)
        self.assertLessEqual(value2, value)
        self.assertLessEqual(value2, value2)

    def testParsePositive(self):
        value = Value.parse("3819 USD")
        self.assertEqual(2, value.precision)

    def testParseNegative(self):
        value = Value.parse("-440 EUR")
        self.assertEqual(2, value.precision)

    def testParsePrecision(self):
        value = Value.parse("1.4123 GBP")
        self.assertEqual(4, value.precision)

class MultipleCurrencies(unittest.TestCase):
    def testComponents(self):
        value1 = Value({ "EUR" : Decimal("81.45") })
        value2 = Value({ "USD" : Decimal("-12.44") })
        value = Value({"EUR" : Decimal("81.45"),
                       "USD" : Decimal("-12.44") })
        self.assertItemsEqual([value1, value2], value.components())

if __name__ == '__main__':
    unittest.main()
