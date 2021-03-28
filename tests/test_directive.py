from pledger.account import Account, AccountFactory
from pledger.parser import Parser
from pledger.directive import *
from pledger.ledger_processor import LedgerProcessor
import pytest


class ProcessorStub(object):
    def __init__(self):
        self.repo = AccountFactory()
        self.account = self.repo.root()
        self.included = []

    def add_account_prefix(self, prefix):
        self.account = self.account[prefix]

    def remove_account_prefix(self):
        self.account = self.account.parent

    def include(self, filename):
        self.included.append(filename)


@pytest.fixture
def processor(parser):
    return ProcessorStub()


def test_directive_registry():
    assert Directive.directives['account'] == AccountDirective
    assert Directive.directives.get('non-existing-directive') is None


def test_unsupported_directive(parser):
    with pytest.raises(UnsupportedDirective) as e:
        parser.parse_directive("!nonexisting")

    assert 'nonexisting' == str(e.value)


def test_account_directive(processor):
    directive = AccountDirective("Assets")
    assert processor.account.name == ""
    directive.execute(processor)
    assert processor.account.name == "Assets"


def test_end_account_directive(processor):
    directive = EndAccountDirective()
    processor.add_account_prefix("Assets")
    directive.execute(processor)
    assert processor.account.name == ""


def test_include_directive(processor):
    directive = IncludeDirective("test.dat")
    assert processor.included == []
    directive.execute(processor)
    assert processor.included == ["test.dat"]


def test_directive_parsing(parser):
    directive = parser.parse_directive("!include test.dat")
    assert directive.filename == "test.dat"
