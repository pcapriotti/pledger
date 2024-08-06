from datetime import datetime
from .tags import has_tag

COLORS = {
    "bold_white": "\033[1;37m",
    "red": "\033[0;31m",
    "yellow": "\033[0;33m",
    "green": "\033[0;32m",
    "nocolor": "\033[00m",
    "blue": "\033[0;34m",
}


class Layout:
    def __init__(self, description, account):
        self.description = description
        self.account = account


class Template(object):
    ACCOUNT_COLOR = "blue"

    def __call__(self, width, ledgers, report, output):
        layout = Layout(width // 4, width // 4)
        for line in self.generate(layout, ledgers, report):
            output(line)

    def pad(self, item, size, color=None):
        text = str(item)[:size]
        padlength = size - len(text)
        if padlength < 0:
            padlength = 0
        return "%s%s" % (" " * padlength, self.colored(color, text))

    def lpad(self, item, size, color=None):
        text = str(item)[:size]
        padlength = size - len(text)
        if padlength < 0:
            padlength = 0
        return "%s%s" % (self.colored(color, text), " " * padlength)

    def print_value(self, value):
        if value:
            text = str(value)
            color = None
            if value.negative():
                color = "red"
            return self.pad(text, 20, color)
        else:
            return ""

    def print_account(self, account, size):
        if size is None:
            return self.colored(self.ACCOUNT_COLOR, account.name)
        else:
            text = account.shortened_name(size)
            return self.lpad(text, size, self.ACCOUNT_COLOR)

    def print_label(self, transaction, size):
        color = None
        if not has_tag(transaction, "cleared"):
            color = "bold_white"
        return self.lpad(transaction.label, size, color)

    def colored(self, color, text):
        if color:
            return COLORS[color] + text + COLORS["nocolor"]
        else:
            return text


class BalanceTemplate(Template):
    def generate(self, layout, ledgers, report):
        it = report.generate(ledgers)
        # save total
        total = next(it)
        count = 0
        for entry in it:
            components = entry.amount.components()
            for component in components[:-1]:
                yield self.print_value(component)
            yield self.print_value(components[-1]) + (
                "  " * (entry.level - 1)
            ) + self.colored(self.ACCOUNT_COLOR, entry.account)
            count += 1
        if count > 0:
            yield "-" * 20
            for component in total.amount.components():
                yield self.print_value(component)


class RegisterTemplate(Template):
    def generate(self, layout, ledgers, report):
        last_entry = None
        for entry in report.generate(ledgers):
            if last_entry and id(last_entry.transaction) == id(entry.transaction):
                for line in self.print_secondary_entry(layout, entry):
                    yield line
            else:
                for line in self.print_entry(layout, entry):
                    yield line
            last_entry = entry

    def print_entry(self, layout, entry):
        currencies = sorted(
            set(entry.entry.amount.currencies()).union(entry.total.currencies())
        )
        components = entry.entry.amount.components(currencies)
        total_components = entry.total.components(currencies)
        yield "%s %s %s %s %s" % (
            self.lpad(entry.date.strftime("%y-%b-%d"), 9),
            self.print_label(entry.transaction, layout.description),
            self.print_account(entry.entry.account, layout.account),
            self.print_value(components[0]),
            self.print_value(total_components[0]),
        )
        for line in self.print_extra_components(
            layout, entry, components[1:], total_components[1:]
        ):
            yield line

    def print_secondary_entry(self, layout, entry):
        currencies = sorted(
            set(entry.entry.amount.currencies()).union(entry.total.currencies())
        )
        components = entry.entry.amount.components(currencies)
        total_components = entry.total.components(currencies)
        yield "%s %s %s %s" % (
            " " * (layout.description + 10),
            self.print_account(entry.entry.account, layout.account),
            self.print_value(components[0]),
            self.print_value(total_components[0]),
        )
        for line in self.print_extra_components(
            layout, entry, components[1:], total_components[1:]
        ):
            yield line

    def print_extra_components(self, layout, entry, components, total_components):
        for i in range(len(components)):
            yield "%s %s %s" % (
                " " * (layout.description + layout.account + 11),
                self.print_value(components[i]),
                self.print_value(total_components[i]),
            )


def default_template(width, ledgers, report, *args):
    return report.template(width, ledgers, report, *args)
