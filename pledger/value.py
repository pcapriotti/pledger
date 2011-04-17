from decimal import Decimal, InvalidOperation
import re

class Value(object):
    def __init__(self, values):
        self.values = values

    def __eq__(self, other):
        return self.values == other.values

    def __add__(self, other):
        result = dict(self.values)
        for currency in other.values:
            amount = other.values[currency]
            if currency in result:
                result[currency] += amount
            else:
                result[currency] = amount
        return Value(result)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        result = { }
        for currency in self.values:
            result[currency] = -self.values[currency]
        return Value(result)

    def format_value(self, curr, value, places=2):
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
            if i == 3 and digits:
                i = 0
                build(sep)
        if sign: build('-')
        return ''.join(reversed(result))

    def __str__(self, places=2):
        return ", ".join([self.format_value(curr, value) for
                          curr, value in self.values.iteritems()])

    def __repr__(self): return str(self)

    @classmethod
    def parse(cls, str):
        elements = re.split(r"\s+", str)
        if len(elements) == 2:
            try:
                amount = Decimal(elements[0])
                currency = elements[1]
                return Value({ currency: amount })
            except InvalidOperation:
                return None

ZERO = Value({})
