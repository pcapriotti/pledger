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
from pledger.util import struct, linearized, PrefixTree
from pledger.template import BalanceTemplate, RegisterTemplate
from pledger.ledger_processor import LedgerProcessor

class BalanceEntryProcessor(object):
    Entry = struct("level", "account", "amount")

    def __init__(self):
        self.sheet = { }
        self.total = ZERO

    def process_entry(self, transaction, entry):
        self.add_entry(entry.account, entry.amount)

    def add_entry(self, account, amount):
        self.sheet.setdefault(account, ZERO)
        self.sheet[account] += amount
        if account.parent:
            self.add_entry(account.parent, amount)
        else:
            self.total += amount

    def accounts(self):
        grouped = self.grouped_accounts(None, 0, sorted(self.sheet.keys()))
        if len(grouped) > 0:
            root, items = grouped[0]
            return linearized(items)
        else:
            return []

    def grouped_accounts(self, root, level, accounts, prefix = ""):
        children = [account for account in accounts if account.parent == root]
        if len(children) == 1 and root and root.base_name and self.sheet[root] == self.sheet[children[0]]:
            return self.grouped_accounts(children[0], level, accounts, prefix + root.base_name + ":")
        else:
            result = [self.grouped_accounts(child, level + 1, accounts) for child in children]
            if root:
                return ((root, prefix + str(root.base_name), level), result)
            else:
                return result

    def post_process(self):
        pass

    @property
    def result(self):
        yield self.__class__.Entry(level=None,
                                   account=None,
                                   amount=self.total)
        for account, name, level in self.accounts():
            yield self.__class__.Entry(level=level,
                                       account=name,
                                       amount=self.sheet[account])

class RegisterEntryProcessor(object):
    class Entry(struct("transaction", "entry", "total")):
        @property
        def date(self):
            return self.entry.date(self.transaction)

    def __init__(self, sorting):
        self.unsorted_result = []
        self.total = ZERO
        self.sorting = sorting

    def process_entry(self, transaction, entry):
        e = RegisterEntryProcessor.Entry(
                transaction=transaction,
                entry=entry,
                total=ZERO)
        self.unsorted_result.append(e)

    def post_process(self):
        self.result = self.sorting(self.unsorted_result)
        total = ZERO
        for entry in self.result:
            total += entry.entry.amount
            entry.total = total

class Report(object):
    def __init__(self, ledger, rules, filter, entry_processor, template):
        self.ledger_processor = LedgerProcessor(ledger, rules)
        self.ledger_processor.add_listener(self)
        self.filter = filter
        self.entry_processor = entry_processor
        self.template = template

    def generate(self):
        self.ledger_processor.run()
        self.entry_processor.post_process()
        return self.result()

    def on_transaction(self, transaction, entries):
        for entry in entries:
            if self.filter(transaction, entry):
                self.entry_processor.process_entry(transaction, entry)

    def result(self):
        return self.entry_processor.result

    @classmethod
    def balance(cls, ledger, rules, filter, sorting):
        return cls(ledger, rules, filter, BalanceEntryProcessor(),
                template=BalanceTemplate())

    @classmethod
    def register(cls, ledger, rules, filter, sorting):
        return cls(ledger, rules, filter, RegisterEntryProcessor(sorting),
                template=RegisterTemplate())

class ReportRegistry(object):
    def __init__(self, reps):
        self.reps = reps
        self.prefix_tree = PrefixTree(reps.keys())

    def get(self, prefix):
        candidates = self.prefix_tree.from_prefix(prefix)
        if len(candidates) == 1:
            return self.reps[candidates[0]]

    def __getitem__(self, name):
        return self.reps[name]

    def add(self, name, factory):
        if name in self.reps:
            raise Exception.new("Report %s already exists" % name)
        self.reps[name] = factory
        self.prefix_tree.insert(name)

reports = ReportRegistry({
    "balance" : Report.balance,
    "register" : Report.register
})
