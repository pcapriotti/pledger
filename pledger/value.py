from decimal import Decimal, InvalidOperation, ROUND_DOWN
import re

class Value(object):
    def __init__(self, values, precision=2):
        self.values = values
        self.precision = precision

    def currencies(self):
        return (currency for currency,amount in self.values.iteritems() if amount != 0)

    def component(self, currency):
        amount = self.values.get(currency, 0)
        if amount:
            return Value({currency: amount})

    def null(self):
        for currency, amount in self.values.iteritems():
            if amount != 0: return False
        return True

    def negative(self):
        for currency, amount in self.values.iteritems():
            if amount > 0: return False
        return not self.null()

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return (self - other).null()

    def __add__(self, other):
        result = dict(self.values)
        for currency in other.values:
            amount = other.values[currency]
            if currency in result:
                result[currency] += amount
            else:
                result[currency] = amount
        return Value(result, max(self.precision, other.precision))

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        result = { }
        for currency in self.values:
            result[currency] = -self.values[currency]
        return Value(result, self.precision)

    def __mul__(self, num):
        result = { }
        for currency in self.values:
            unit = Decimal(10) ** -self.precision
            result[currency] = (self.values[currency] * num).quantize(unit)
        return Value(result, self.precision)

    def __lt__(self, other):
        return (self - other).negative()

    def __gt__(self, other):
        return (other - self).negative()

    def format_value(self, curr, value):
        places = self.precision
        q = Decimal(10) ** -places      # 2 places --> '0.01'
        sign, digits, exp = value.quantize(q).as_tuple()
        result = []
        digits = map(str, digits)
        build, next = result.append, digits.pop
        build(" " + curr)
        for i in range(places):
            build(next() if digits else '0')
        build('.')
        if not digits:
            build('0')
        i = 0
        while digits:
            build(next())
            i += 1
        if sign: build('-')
        return ''.join(reversed(result))

    def __str__(self):
        if self.null():
            return "0"
        else:
            return ", ".join([self.format_value(curr, value) for
                              curr, value in self.values.iteritems()])

    def __repr__(self): return str(self)

    @classmethod
    def parse(cls, str, precision):
        elements = re.split(r"\s+", str)
        if len(elements) == 2:
            try:
                amount = Decimal(elements[0])
                currency = elements[1]
                return Value({ currency: amount }, precision=precision)
            except InvalidOperation:
                return None

ZERO = Value({}, 0)
