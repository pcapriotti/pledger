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

    def __str__(self):
        return "%s (%s)" % (self.account, self.amount)
