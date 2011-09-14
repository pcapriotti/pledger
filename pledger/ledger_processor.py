# Copyright (C) 2011 by Paolo Capriotti <p.capriotti@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pledger.value import ZERO
from pledger.entry import Entry
from pledger.transaction import Transaction
from pledger.util import Observable
from collections import OrderedDict

class LedgerProcessor(Observable):
    def __init__(self, ledger, rules, transaction_rules):
        super(LedgerProcessor, self).__init__()
        self.ledger = ledger
        self.rules = rules
        self.transaction_rules = transaction_rules
        self.parser = self.ledger.parser
        self.account = self.parser.accounts

    def run(self):
        for transaction in self.ledger.transactions:
            transaction.execute(self)

    def add_account_prefix(self, prefix):
        self.account = self.account[prefix]

    def remove_account_prefix(self):
        self.account = self.account.parent

    def add_transaction(self, transaction):
        entries = self.filter(transaction)
        t = self.process_transaction(transaction, entries)
        self.fire("transaction", t, entries)

    def include(self, filename):
        filename = self.ledger.absolute_filename(filename)
        subledger = self.parser.parse_ledger(filename)
        self.create_child(subledger).run()

    def filter(self, transaction):
        result = []
        for entry in transaction.entries:
            account = self.account[entry.account.name]
            amount = entry.amount
            result += self.rules.apply(transaction, Entry(account, amount, tags=entry.tags))
        return self.compact(result)

    def process_transaction(self, transaction, entries):
        result = Transaction(entries, transaction.date, transaction.label, transaction.tags)
        for rule in self.transaction_rules:
            result = rule.apply(result)
        return result

    def create_child(self, ledger):
        child = self.__class__(ledger, self.rules, self.transaction_rules)
        child.account = self.account
        child.listeners = self.listeners
        return child

    def compact(self, entries):
        result = OrderedDict()
        for entry in entries:
            key = (entry.account, tuple(sorted(entry.tags.items())))
            e = result.get(key)
            if e:
                e.amount += entry.amount
            else:
                result[key] = Entry(entry.account, entry.amount, entry.tags)
        return result.values()
