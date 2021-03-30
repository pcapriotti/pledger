from .value import ZERO
from .util import linearized, PrefixTree
from .template import BalanceTemplate, RegisterTemplate
from .ledger_processor import LedgerProcessor
from collections import namedtuple


class BalanceEntryProcessor(object):
    Entry = namedtuple("Entry", "level account amount")

    def __init__(self):
        self.sheet = {}
        self.total = ZERO

    def process_entry(self, transaction, entry):
        self.add_entry(entry.account, entry.amount)

    def add_entry(self, account, amount):
        self.sheet.setdefault(account.path, ZERO)
        self.sheet[account.path] += amount
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

    def grouped_accounts(self, root, level, paths, prefix=""):
        children = [path for path in paths if path.parent == root]
        if len(children) == 1 and root and \
           root.base_name and \
           self.sheet[root] == self.sheet[children[0]]:
            return self.grouped_accounts(children[0], level, paths,
                                         prefix + root.base_name + ":")
        else:
            result = [self.grouped_accounts(child, level + 1, paths)
                      for child in children]
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
    class Entry(namedtuple("Entry_", "transaction entry total")):
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
        total = ZERO
        self.result = []
        for record in self.sorting(self.unsorted_result):
            total += record.entry.amount
            self.result.append(record._replace(total=total))


class Report(object):
    def __init__(self, parser, rules, filter, entry_processor, template):
        self.ledger_processor = LedgerProcessor(parser, rules)
        self.ledger_processor.add_listener(self)
        self.filter = filter
        self.entry_processor = entry_processor
        self.template = template

    def generate(self, ledgers):
        for ledger in ledgers:
            self.ledger_processor.run(ledger)
        self.entry_processor.post_process()
        return self.result()

    def on_transaction(self, transaction, entries):
        for entry in entries:
            if self.filter(transaction, entry):
                self.entry_processor.process_entry(transaction, entry)

    def result(self):
        return self.entry_processor.result

    @classmethod
    def balance(cls, parser, rules, filter, sorting):
        return cls(parser, rules, filter, BalanceEntryProcessor(),
                   template=BalanceTemplate())

    @classmethod
    def register(cls, parser, rules, filter, sorting):
        return cls(parser, rules, filter, RegisterEntryProcessor(sorting),
                   template=RegisterTemplate())


class ReportRegistry(object):
    def __init__(self, reps):
        self.reps = reps
        self.prefix_tree = PrefixTree(list(reps.keys()))

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
    "balance": Report.balance,
    "register": Report.register
})
