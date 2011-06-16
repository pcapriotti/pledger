from datetime import datetime

COLORS = {
    "bold_white" : "\033[1;37m",
    "red" : "\033[0;31m",
    "yellow" : "\033[0;33m",
    "green" : "\033[0;32m",
    "nocolor" : "\033[00m",
    "blue" : "\033[0;34m" }

class Template(object):
    def pad(self, item, size, color = None):
        text = unicode(item)[:size]
        padlength = size - len(text)
        if (padlength < 0): padlength = 0
        return u"%s%s" % (" " * padlength, self.colored(color, text))

    def lpad(self, item, size, color = None):
        text = unicode(item)[:size]
        padlength = size - len(text)
        if (padlength < 0): padlength = 0
        return u"%s%s" % (self.colored(color, text), " " * padlength)

    def print_value(self, value):
        if value:
            text = unicode(value)
            color = None
            if value.negative():
                color = "red"
            return self.pad(text, 20, color)
        else:
            return ""

    def print_account(self, account, size=39):
        if size is None:
            return self.colored("blue", account)
        else:
            text = account.shortened_name(size)
            return self.lpad(text, size, "blue")

    def print_label(self, transaction, size):
        color = None
        if not transaction.has_tag("cleared"):
            color = "bold_white"
        return self.lpad(transaction.label, size, color)

    def colored(self, color, text):
        if color:
            return COLORS[color] + text + COLORS["nocolor"]
        else:
            return text

class BalanceTemplate(Template):
    def __call__(self, report):
        it = report.generate()
        # save total
        total = it.next()
        for entry in it:
            currencies = sorted(entry.amount.currencies())
            for currency in currencies[:-1]:
                yield self.print_value(entry.amount.component(currency))
            yield self.print_value(entry.amount.component(currencies[-1])) + \
                  ("  " * (entry.level - 1)) + \
                  self.print_account(entry.account, None)
        yield u"-" * 20
        currencies = sorted(total.amount.currencies())
        for currency in currencies:
            yield self.print_value(total.amount.component(currency))

class RegisterTemplate(Template):
    def __call__(self, report):
        last_entry = None
        for entry in report.generate():
            if last_entry and id(last_entry.transaction) == id(entry.transaction):
                for line in self.print_secondary_entry(entry):
                    yield line
            else:
                for line in self.print_entry(entry):
                    yield line
            last_entry = entry

    def print_entry(self, entry):
        currencies = sorted(set(entry.entry.amount.currencies()).union(entry.total.currencies()))
        yield u"%s %s %s %s %s" % (
            self.lpad(datetime.strftime(entry.date, "%y-%b-%d"), 9),
            self.print_label(entry.transaction, 34),
            self.print_account(entry.entry.account),
            self.print_value(entry.entry.amount.component(currencies[0])),
            self.print_value(entry.total.component(currencies[0])))
        for line in self.print_extra_components(entry, currencies[1:]):
            yield line

    def print_secondary_entry(self, entry):
        currencies = sorted(set(entry.entry.amount.currencies()).union(entry.total.currencies()))
        yield u"%s %s %s %s" % (
            " " * 44,
            self.print_account(entry.entry.account),
            self.print_value(entry.entry.amount.component(currencies[0])),
            self.print_value(entry.total.component(currencies[0])))
        for line in self.print_extra_components(entry, currencies[1:]):
            yield line

    def print_extra_components(self, entry, currencies):
        for currency in currencies:
            yield u"%s %s %s" % (
                " " * 104,
                self.print_value(entry.entry.amount.component(currency)),
                self.print_value(entry.total.component(currency)))

def default_template(report):
    return report.template(report)
