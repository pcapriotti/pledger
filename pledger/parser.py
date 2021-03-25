import itertools
import re
import codecs
from datetime import datetime, date
from .account import AccountRepository, NamedAccount
from .value import Value
from .ledger import Ledger
from .transaction import Transaction, UndefinedTransaction, UnbalancedTransaction
from .directive import Directive, UnsupportedDirective
from .entry import Entry
from .util import PledgerException, itersplit

date_formats = {
    "default": "%Y/%m/%d",
    "year": "%Y",
    "month": "%b" }

class MalformedHeader(PledgerException):
    pass

class Parser(object):
    def __init__(self):
        self.accounts = AccountRepository()
        self.precision = 2

    def parse_account(self, str):
        return self.accounts[str]

    def parse_value(self, str):
        return Value.parse(str)

    def parse_ledger(self, filename, str = None):
        if str is None:
            str = codecs.open(filename, "r", "utf-8").read()
        f = lambda number_line: number_line[1] == ""
        lines = zip(itertools.count(1), str.split("\n"))
        try:
            transactions = [self.parse_transaction(group) for group in itersplit(f, lines)]
        except PledgerException as e:
            e.filename = filename
            raise e
        return Ledger(filename, [t for t in transactions if t], self)

    def parse_entry(self, str):
        tags = self.parse_tags(str)
        str = re.sub(";.*$", "", str)

        elements = [e for e in re.split(r"  +", str) if e]
        if len(elements) >= 1:
            account = self.parse_account(elements[0])
            amount = None
            if len(elements) >= 2:
                amount = self.parse_value(elements[1])
            if account:
                return Entry(account, amount, tags)

    def parse_transaction(self, lines):
        if hasattr(lines, "split"):
            lines = list(zip(itertools.count(1), iter(lines.split("\n"))))

        tags = { }

        # discard initial comments
        while lines and re.match(r'\s*;', lines[0][1]):
            lines = lines[1:]

        if len(lines) == 0:
            return None

        n, header = lines[0]
        lines = lines[1:]

        # skip rules
        if len(header) == 0 or header[0] == "=":
            return None

        directive = self.parse_directive(header)
        if directive: return directive

        # parse transaction tags
        if lines:
            n, line = lines[0]
            tags = self.parse_tags(line, begin=True)
            if tags: lines = lines[1:]

        try:
            date, label, cleared = self.parse_header(header)
            date = self.parse_date(date)
            if date is None:
                raise MalformedHeader()

            entries = [self.parse_entry(line) for n, line in lines]
            line_numbers = [n for n, line in lines]
            transaction = Transaction(entries, date, label)
            if tags: transaction.tags = tags
            if cleared: transaction.tags["cleared"] = True
            return transaction
        except UnbalancedTransaction as e:
            e.line_number = n
            raise e
        except UndefinedTransaction as e:
            e.line_number = line_numbers[e.index]
            raise e
        except MalformedHeader as e:
            e.line_number = n
            raise e

    def parse_date(self, str, format="default"):
        try:
            return datetime.strptime(str, date_formats[format]).date()
        except ValueError:
            pass

    def parse_month(self, str):
        base = self.parse_date(str, "month")
        if base: return date(date.today().year, base.month, 1)

    def parse_year(self, str):
        base = self.parse_date(str, "year")
        if base: return date(base.year, 1, 1)

    def parse_fuzzy_date(self, str):
        for parser in [self.parse_date, self.parse_month, self.parse_year]:
            result = parser(str)
            if result: return result
        return None

    def parse_header(self, str):
        m = re.match(r'^(\S+)\s+(\*\s+)?(.*)$', str)
        if m:
            return m.group(1), m.group(3), m.group(2)
        else:
            raise MalformedHeader()

    def parse_tags(self, str, begin=False):
        pattern = r'\s*;\s*(.*)$'
        if begin:
            m = re.match(pattern, str)
        else:
            m = re.search(pattern, str)
        if m:
            tagstring = m.group(1)
            tag_dict = []
            while True:
                result = self.parse_tag(tagstring)
                if result is None: break
                tag, index = result
                tag_dict.append(tag)
                tagstring = tagstring[index:]
            return dict(tag_dict)

    def parse_tag(self, str):
        m = re.match(r':?(\S+):"([^"]*)"\s*', str)
        if m:
            return ((m.group(1), m.group(2)), m.end())
        m = re.match(r":?(\S+):'([^']*)'\s*", str)
        if m:
            return ((m.group(1), m.group(2)), m.end())
        m = re.match(r':?(\S+):(\S*)\s*', str)
        if m:
            return ((m.group(1), m.group(2)), m.end())
        m = re.match(r'\[(\S+)\]\s*', str)
        if m:
            try:
                return (("date", self.parse_date(m.group(1))), m.end())
            except ValueError:
                pass

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
