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

from datetime import datetime

COLORS = {
    "bold_white" : "\033[1;37m",
    "red" : "\033[0;31m",
    "yellow" : "\033[0;33m",
    "green" : "\033[0;32m",
    "nocolor" : "\033[00m",
    "blue" : "\033[0;34m" }

class Template(object):
    def __call__(self, report, output):
        for line in self.generate(report):
            output(line)

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
    def generate(self, report):
        it = report.generate()
        # save total
        total = it.next()
        count = 0
        for entry in it:
            components = entry.amount.components()
            for component in components[:-1]:
                yield self.print_value(component)
            yield self.print_value(components[-1]) + \
                  ("  " * (entry.level - 1)) + \
                  self.print_account(entry.account, None)
            count += 1
        if count > 0:
            yield u"-" * 20
            for component in total.amount.components():
                yield self.print_value(component)

class RegisterTemplate(Template):
    def generate(self, report):
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
        components = entry.entry.amount.components(currencies)
        total_components = entry.total.components(currencies)
        yield u"%s %s %s %s %s" % (
            self.lpad(entry.date.strftime("%y-%b-%d"), 9),
            self.print_label(entry.transaction, 34),
            self.print_account(entry.entry.account),
            self.print_value(components[0]),
            self.print_value(total_components[0]))
        for line in self.print_extra_components(entry, components[1:], total_components[1:]):
            yield line

    def print_secondary_entry(self, entry):
        currencies = sorted(set(entry.entry.amount.currencies()).union(entry.total.currencies()))
        components = entry.entry.amount.components(currencies)
        total_components = entry.total.components(currencies)
        yield u"%s %s %s %s" % (
            " " * 44,
            self.print_account(entry.entry.account),
            self.print_value(components[0]),
            self.print_value(total_components[0]))
        for line in self.print_extra_components(entry, components[1:], total_components[1:]):
            yield line

    def print_extra_components(self, entry, components, total_components):
        for i in xrange(len(components)):
            yield u"%s %s %s" % (
                " " * 104,
                self.print_value(components[i]),
                self.print_value(total_components[i]))

def default_template(report, *args):
    return report.template(report, *args)
