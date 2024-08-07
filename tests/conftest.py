from pledger.account import AccountFactory
from pledger.parser import Parser
from pledger.rule import RuleCollection
import os
import pytest


@pytest.fixture
def parser():
    return Parser()


@pytest.fixture
def named_account(parser):
    def f(name):
        return parser.parse_account(name)

    return f


@pytest.fixture
def data_dir(request):
    return os.path.join(request.fspath.dirname, "fixtures")


@pytest.fixture
def data_file(data_dir):
    def f(name):
        return os.path.join(data_dir, name)

    return f


@pytest.fixture
def rules():
    return RuleCollection()


@pytest.fixture
def repo():
    return AccountFactory()
