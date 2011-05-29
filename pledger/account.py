from pledger.entry import Entry

class Account(object):
    def __init__(self):
        self.meta = { }

    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

class AccountRepository(object):
    def __init__(self):
        self.accounts = { }

    def get_account(self, name):
        account = self.accounts.get(name)
        if account is None:
            account = NamedAccount(name)
            self.accounts[name] = account
        return account

class NamedAccount(Account):
    def __init__(self, name):
        super(NamedAccount, self).__init__()
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "'%s' (%s)" % (self.name, self.meta)

    def add_prefix(self, prefix):
        name = ":".join(prefix + [self.name])
        return NamedAccount(name)
