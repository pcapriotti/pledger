from datetime import datetime

class Template(object):
    def pad(self, item, size):
        text = unicode(item)
        padlength = size - len(text)
        if (padlength < 0): padlength = 0
        return "%s%s" % (" " * padlength, text)

    def lpad(self, item, size):
        text = unicode(item)
        padlength = size - len(text)
        if (padlength < 0): padlength = 0
        return "%s%s" % (text, " " * padlength)

class BalanceTemplate(Template):
    def __call__(self, report):
        it = report.generate()
        # save total
        total = it.next()
        for entry in it:
            yield self.pad(entry.amount, 20) + ("  " * (entry.level - 1)) + entry.account
        yield "-" * 20
        yield self.pad(total.amount, 20)

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
        return "%s %s %s %s %s" % (
            self.lpad(datetime.strftime(entry.transaction.date, "%y-%b-%d"), 9),
            self.lpad(entry.transaction.label, 34),
            self.lpad(entry.entry.account, 39),
            self.pad(entry.entry.amount, 20),
            self.pad(entry.total, 20))

    def print_secondary_entry(self, entry):
        return "%s %s %s %s" % (
            " " * 44,
            self.lpad(entry.entry.account, 39),
            self.pad(entry.entry.amount, 20),
            self.pad(entry.total, 20))

def default_template(report):
    return report.template(report)
