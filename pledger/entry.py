from dataclasses import dataclass, field, replace


@dataclass(order=True)
class Entry:
    account: object
    amount: object
    tags: dict = field(default_factory=dict)

    def date(self, transaction):
        result = self.tags.get("date")
        if result is None:
            return transaction.date
        else:
            return result

    def info(self, transaction):
        return EntryInfo(
            self.account, self.amount,
            self.tags, self.date(transaction),
            transaction)

    @classmethod
    def from_entry(cls, transaction, entry):
        return entry

    def clone(self):
        return replace(self)


@dataclass(order=True)
class EntryInfo:
    account: object
    amount: object
    tags: dict
    date: object
    parent: object
