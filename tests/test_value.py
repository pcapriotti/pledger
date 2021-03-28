from decimal import Decimal, InvalidOperation
from pledger.value import Value, ZERO
import pytest


def test_sum_null():
    value = Value({"EUR": Decimal(32)})
    assert value + ZERO == value


def test_parsing():
    value = Value({"EUR": Decimal("35.1")})
    assert Value.parse("35.1 EUR") == value


def test_parse_no_currency():
    assert Value.parse("35.1") is None


def test_parse_invalid_decimal():
    assert Value.parse("12.1.1 EUR") is None


def test_currencies():
    value = Value({"EUR": Decimal("21.36")})
    assert list(value.currencies()) == ["EUR"]


def test_components_single():
    value = Value({"EUR": Decimal("31.99")})
    assert list(value.components()) == [value]
    assert list(value.components(["EUR"])) == [value]
    assert list(value.components(["USD"])) == [ZERO]
    assert list(value.components([])) == [ZERO]


def test_neg():
    amount = Decimal("21.36")
    value = Value({"EUR": amount})
    assert -value == Value({"EUR": -amount})


def test_negative():
    value = Value({"EUR": Decimal("31.99")})
    assert not value.negative()
    assert (-value).negative()


def test_equality():
    value = Value({"EUR": Decimal("31.99")})
    value2 = Value({"EUR": Decimal("31.99")})
    value3 = Value({"EUR": Decimal("31.98")})
    assert value == value2
    assert value != value3
    assert not value == None


def test_multiplication():
    value = Value({"EUR": Decimal("31.99")})
    value2 = Value({"EUR": Decimal("63.98")})
    assert value * Decimal(2) == value2
    assert value * Decimal("2.00001") == value2


def test_format():
    value = Value({"EUR": Decimal("31.992371")})
    assert str(value) == "31.99 EUR"
    assert str(ZERO) == "0"


def test_comparison():
    value = Value({"EUR": Decimal("31.99")})
    value2 = Value({"EUR": Decimal("21.36")})
    assert value > value2
    assert value2 < value
    assert value >= value2
    assert value >= value
    assert value2 <= value
    assert value2 <= value2


def test_parse_positive():
    value = Value.parse("3819 USD")
    assert value.precision == 2


def test_parse_negative():
    value = Value.parse("-440 EUR")
    assert value.precision == 2


def test_parse_precision():
    value = Value.parse("1.4123 GBP")
    assert value.precision == 4


def test_components():
    value1 = Value({"EUR": Decimal("81.45")})
    value2 = Value({"USD": Decimal("-12.44")})
    value = Value({"EUR": Decimal("81.45"),
                   "USD": Decimal("-12.44")})
    assert value.components() == [value1, value2]
