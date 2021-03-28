from collections import defaultdict
from dataclasses import dataclass

from .entry import Entry
from .filter import Filter
from .rule import Generator, Rule


@dataclass(frozen=True, order=True)
class AccountPath:
    components: tuple
    absolute: bool

    @classmethod
    def root(cls):
        return cls((), absolute=True)

    @classmethod
    def parse(cls, name):
        absolute = name.startswith('::')
        if absolute:
            name = name[2:]
        return cls(tuple(name.split(':')), absolute)

    @property
    def base_name(self):
        if self.components:
            return self.components[-1]

    def __str__(self):
        return ":".join(self.components)

    @property
    def parent(self):
        if self.components:
            return type(self)(self.components[:-1], self.absolute)

    def __getitem__(self, name):
        path = type(self).parse(name)
        return self.sub(path)

    def shortened(self, size):
        full = str(self)
        delta = len(full) - size
        if delta <= 0:
            return full
        n = len(self.components)
        component_delta = (delta + n - 1) // n
        extra = delta - component_delta * n
        c1 = [x[:len(x) - component_delta - 1]
              for x in self.components[:extra]]
        c2 = [x[:len(x) - component_delta] for x in self.components[extra:-1]]
        c3 = [self.components[-1]]
        return ":".join(c1 + c2 + c3)

    def is_ancestor(self, other):
        return all(self.components[i] == other.components[i]
                   for i in range(len(self.components)))

    def sub(self, path):
        if path.absolute:
            return path
        return self.__class__(self.components + path.components,
                              self.absolute)


class AccountFactory:
    def __init__(self):
        self.tags = defaultdict(dict)

    def __call__(self, path):
        if path is not None:
            return Account(path, self)

    def parse(self, name):
        return self(AccountPath.parse(name))

    def root(self):
        return self(AccountPath.root())


class Account:
    def __init__(self, path, repo):
        self.path = path
        self.repo = repo

    def __eq__(self, other):
        return (self.path, self.repo) \
            == (other.path, other.repo)

    @property
    def tags(self):
        return self.repo.tags[self.path]

    @property
    def parent(self):
        return self.repo(self.path.parent)

    def __getitem__(self, name):
        return self.repo(self.path[name])

    def sub(self, path):
        return self.repo(self.path.sub(path))

    @property
    def name(self):
        return str(self.path)

    def shortened_name(self, size):
        return self.path.shortened(size)

    @classmethod
    def from_entry(cls, transaction, entry):
        return entry.account

    @classmethod
    def tag_rule(cls, tag, filter=Filter.null):
        @Generator
        def generator(entry):
            gen = entry.account.tags.get(tag)
            if gen:
                yield from gen(entry)
        return Rule(filter, generator)

    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

    def filter(self):
        @Filter
        def result(transaction, entry):
            return self.path.is_ancestor(entry.account.path)
        return result
