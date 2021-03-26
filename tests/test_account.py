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

def test_root(parser, account):
    assert account.root() == parser.accounts["Assets"]

def test_shortened_name(account):
    account = account["Joint:Savings:Yearly:Interest:Compound:Open"]
    size = 30
    name = account.shortened_name(size)

    assert len(name) < size
    assert len([x for x in name if x == ':']) == 7

def test_sub_name(parser, account):
    checking = account["Checking"]
    assert account.parent.sub_name(checking) == "Bank:Checking"
    assert account.sub_name(parser.accounts["Test"]) is None

def test_root_account_parsing(parser, account):
    loan = account["::Liabilities:Loan"]
    assert loan.name == "Liabilities:Loan"
