class BalanceTemplate(object):
    def __call__(self, report):
        result = ""
        for entry in report:
            result += self.pad(entry.amount, 20) + ("  " * entry.level) + entry.account + "\n"
        return result

    def pad(self, item, size):
        text = str(item)
        padlength = size - len(text)
        if (padlength < 0): padlength = 0
        return "%s%s" % (" " * padlength, text)
