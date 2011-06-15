import itertools
import re
import codecs
from datetime import datetime
from pledger.account import AccountRepository, NamedAccount
from pledger.value import Value
from pledger.ledger import Ledger
from pledger.transaction import Transaction, UndefinedTransaction, UnbalancedTransaction
from pledger.directive import Directive, UnsupportedDirective
from pledger.entry import Entry
from pledger.util import PledgerException, itersplit

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
        return NamedAccount(str)

    def parse_value(self, str):
        return Value.parse(str, precision=self.precision)

    def parse_ledger(self, filename, str = None):
        if str is None:
            str = codecs.open(filename, "r", "utf-8").read()
        f = lambda (number, line): line == ""
        lines = itertools.izip(itertools.count(1), str.split("\n"))
        try:
            transactions = [self.parse_transaction(group) for group in itersplit(f, lines)]
        except PledgerException, e:
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
            lines = list(itertools.izip(itertools.count(1), iter(lines.split("\n"))))

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
            date, label = self.parse_header(header)
            date = self.parse_date(date)

            entries = [self.parse_entry(line) for n, line in lines]
            line_numbers = [n for n, line in lines]
            transaction = Transaction(entries, date, label)
            if tags: transaction.tags = tags
            return transaction
        except UnbalancedTransaction, e:
            e.line_number = n
            raise e
        except UndefinedTransaction, e:
            e.line_number = line_numbers[e.index]
            raise e
        except MalformedHeader, e:
            e.line_number = n
            raise e
        except ValueError, e:
            e = MalformedHeader()
            e.line_number = n
            raise e

    def parse_date(self, str, format="default"):
        try:
            return datetime.strptime(str, date_formats[format]).date()
        except ValueError:
            pass

    def parse_month(self, str):
        try:
            month = self.parse_date(str, "month")
            current = date.today()
            return date(current.year, month, 1)
        except ValueError:
            pass

    def parse_year(self, str):
        try:
            year = self.parse_date(str, "year")
            return date(year, 1, 1)
        except ValueError:
            pass

    def parse_fuzzy_date(self, str):
        result = None
        for parser in [self.parse_date, self.parse_month, self.parse_year]:
            result = parser(str)
            if result: return result
        return None

    def parse_header(self, str):
        m = re.match(r'^(\S+)\s+(\*\s+)?(.*)$', str)
        if m:
            return m.group(1), m.group(3)
        else:
            raise MalformedHeader()

    def parse_tags(self, str, begin=False):
        pattern = r'\s*;\s*(.*)$'
        if begin:
            m = re.match(pattern, str)
        else:
            m = re.search(pattern, str)
        if m:
            tags = re.split(r'\s+', m.group(1))
            tag_dict = []
            for str in tags:
                tag = self.parse_tag(str)
                if tag: tag_dict.append(tag)
            return dict(tag_dict)

    def parse_tag(self, str):
        m = re.match(r':?(\S+):(\S*)$', str)
        if m:
            return (m.group(1), m.group(2))
        m = re.match(r'\[(\S+)\]$', str)
        if m:
            try:
                return ("date", self.parse_date(m.group(1)))
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
