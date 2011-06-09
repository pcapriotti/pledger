import itertools
import re
import util
from datetime import datetime
from pledger.account import AccountRepository, NamedAccount
from pledger.value import Value
from pledger.ledger import Ledger
from pledger.transaction import Transaction
from pledger.directive import Directive, UnsupportedDirective
from pledger.entry import Entry

class UnbalancedTransaction(Exception):
    def __init__(self, tr):
        self.tr = tr

class UndefinedTransaction(Exception):
    def __init__(self, tr, index):
        self.tr = tr
        self.index = index

class MalformedHeader(Exception):
    pass


class Parser(object):
    def __init__(self):
        self.accounts = AccountRepository()

    def parse_account(self, str):
        return NamedAccount(str)

    def parse_value(self, str):
        return Value.parse(str)

    def parse_ledger(self, str):
        f = lambda (number, line): line == ""

        lines = itertools.izip(itertools.count(1), str.split("\n"))
        transactions = [self.parse_transaction(group) for group in util.itersplit(f, lines)]
        return Ledger([t for t in transactions if t], self)

    def parse_entry(self, str):
        elements = [e for e in re.split(r"  +", str) if e]
        if len(elements) >= 1:
            account = self.parse_account(elements[0])
            amount = None
            if len(elements) >= 2:
                amount = self.parse_value(elements[1])
            if account:
                return Entry(account, amount)

    def parse_transaction(self, str):
        if hasattr(str, "split"):
            lines = itertools.izip(itertools.count(1), iter(str.split("\n")))
        else:
            lines = iter(str)
        lines = ((n, line) for (n, line) in lines if not re.match("\s*;", line))
        try:
            n, header = lines.next()
        except StopIteration:
            return None

        directive = self.parse_directive(header)
        if directive: return directive

        try:
            date, label = self.parse_header(header)
            date = datetime.strptime(date, "%Y/%m/%d")
            entries = [self.parse_entry(line) for n, line in lines]
            line_numbers = [n for n, line in lines]
            return Transaction(entries, date, label)
        except UnbalancedTransaction, e:
            e.line_number = n
            raise e
        except UndefinedTransaction, e:
            e.line_number = line_numbers[e.index]
            raise e
        except MalformedHeader, e:
            e.line_number = n
            print n
            raise e
        except ValueError, e:
            e = MalformedHeader()
            e.line_number = n
            raise e

    def parse_header(self, str):
        m = re.match(r'^(\S+)\s+(\*\s+)?(.*)$', str)
        if m:
            return m.group(1), m.group(3)
        else:
            raise MalformedHeader()

    def parse_directive(self, str):
        if str[0] == '!':
            args = str[1:].split(' ')
            name = args[0]
            args = args[1:]
            directive_class = Directive.directives.get(name)
            if directive_class:
                return directive_class(*args)
            else:
                raise UnsupportedDirective(name)
