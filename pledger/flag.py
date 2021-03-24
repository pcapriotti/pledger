from collections import namedtuple


Flag = namedtuple("Flag", ["name", "args", "filter"])


class FlagMetaclass(type):
    def __new__(cls, name, bases, attrs):
        result = super(FlagMetaclass, cls).__new__(cls, name, bases, attrs)
        name = attrs.get("flag")
        if name:
            args = attrs.get("args", 0)
            f = Flag(name, args, result)
            result.flags.append(f)
        return result
