from datetime import datetime

COLORS = {
    "red" : "\033[0;31m",
    "yellow" : "\033[0;33m",
    "green" : "\033[0;32m",
    "nocolor" : "\033[00m",
    "bold_teal" : "\033[1;36m",
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
        text = unicode(value)
        color = None
        if value.negative():
            color = "red"
        return self.pad(text, 20, color)

    def print_account(self, account, size=39):
        if size is None:
            return self.colored("blue", account)
        else:
            text = account.shortened_name(size)
            return self.lpad(text, size, "blue")

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
            yield self.print_value(entry.amount) + \
                  ("  " * (entry.level - 1)) + \
                  self.print_account(entry.account, None)
        yield u"-" * 20
        yield self.print_value(total.amount)

class RegisterTemplate(Template):
    def __call__(self, report):
        last_entry = None
        for entry in report.generate():
            if last_entry and id(last_entry.transaction) == id(entry.transaction):
                yield self.print_secondary_entry(entry)
            else:
                yield self.print_entry(entry)
            last_entry = entry

    def print_entry(self, entry):
        return u"%s %s %s %s %s" % (
            self.lpad(datetime.strftime(entry.transaction.date, "%y-%b-%d"), 9),
            self.lpad(entry.transaction.label, 34),
            self.print_account(entry.entry.account),
            self.print_value(entry.entry.amount),
            self.print_value(entry.total))

    def print_secondary_entry(self, entry):
        return u"%s %s %s %s" % (
            " " * 44,
            self.print_account(entry.entry.account),
            self.print_value(entry.entry.amount),
            self.print_value(entry.total))

def default_template(report):
    return report.template(report)
