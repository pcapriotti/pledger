from datetime import datetime

class Template(object):
    def pad(self, item, size):
        text = str(item)
        padlength = size - len(text)
        if (padlength < 0): padlength = 0
        return "%s%s" % (" " * padlength, text)

    def lpad(self, item, size):
        text = str(item)
        padlength = size - len(text)
        if (padlength < 0): padlength = 0
        return "%s%s" % (text, " " * padlength)

class BalanceTemplate(Template):
    def __call__(self, report):
        result = ""
        for entry in report.generate():
            result += self.pad(entry.amount, 20) + ("  " * entry.level) + entry.account + "\n"
        return result

class RegisterTemplate(Template):
    def __call__(self, report):
        result = ""
        last_entry = None
        for entry in report.generate():
            if last_entry and id(last_entry.transaction) == id(entry.transaction):
                result += self.print_secondary_entry(entry) + "\n"
            else:
                result += self.print_entry(entry) + "\n"
            last_entry = entry
        return result

    def print_entry(self, entry):
        return "%s %s %s %s %s" % (
            datetime.strftime(entry.transaction.date, "%y-%m-%d"),
            self.lpad(entry.transaction.label, 25),
            self.lpad(entry.entry.account, 60),
            self.pad(entry.entry.amount, 20),
            self.pad(entry.total, 20))

    def print_secondary_entry(self, entry):
        return "%s %s %s %s" % (
            " " * (9 + 25),
            self.lpad(entry.entry.account, 60),
            self.pad(entry.entry.amount, 20),
            self.pad(entry.total, 20))

def default_template(report):
    return report.template(report)
