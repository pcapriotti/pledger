from pledger.parser import Parser

import pytest

@pytest.fixture
def parser():
    return Parser()

@pytest.fixture
def named_account(parser):
    def f(name):
        return parser.parse_account(name)
    return f
