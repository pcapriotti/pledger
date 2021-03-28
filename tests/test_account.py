from pledger.account import AccountPath
from pledger.parser import Parser
import pytest


@pytest.fixture
def account(named_account):
    return named_account("Assets:Bank")


def test_account_add(parser, account):
    amount = parser.parse_value("150 EUR")
    entry = account + amount
    assert entry.account == account
    assert entry.amount == amount


def test_account_sub(parser, account):
    amount = parser.parse_value("150 EUR")
    entry = account - amount
    assert entry.account == account
    assert entry.amount == -amount


def test_path(parser, account):
    assert account.path == AccountPath.parse("Assets:Bank")
    assert account.path.components == ("Assets", "Bank")


def test_shortened_name(account):
    account = account["Joint:Savings:Yearly:Interest:Compound:Open"]
    size = 30
    name = account.shortened_name(size)

    assert len(name) < size
    assert len([x for x in name if x == ':']) == 7


def test_root_account_parsing(parser, account):
    loan = account["::Liabilities:Loan"]
    assert loan.name == "Liabilities:Loan"
