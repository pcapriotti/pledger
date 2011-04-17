import re
from pledger.account import Account
from pledger.value import Value

class Entry(object):
    def __init__(self, account, amount):
        self.account = account
        self.amount = amount

    def __eq__(self, other):
        return self.account == other.account and \
               self.amount == other.amount

    @classmethod
    def parse(cls, str):
        elements = [e for e in re.split(r"  +", str) if e]
        if len(elements) == 2:
            account = Account.parse(elements[0])
            amount = Value.parse(elements[1])
            if account and amount:
                return cls(account, amount)
