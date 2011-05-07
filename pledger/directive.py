class DirectiveMetaclass(type):
    def __new__(cls, name, bases, attrs):
        result = super(DirectiveMetaclass, cls).__new__(cls, name, bases, attrs)
        if name != "Directive":
            Directive.directives[attrs['keyword']] = result
        return result

class UnsupportedDirective(Exception):
    def __init__(self, name):
        self.name = name

class Directive(object):
    __metaclass__ = DirectiveMetaclass

    @classmethod
    def parse(cls, str):
        if str[0] == '!':
            args = str[1:].split(' ')
            name = args[0]
            args = args[1:]
            directive_class = cls.directives[name]
            if directive_class:
                return directive_class(*args)
            else:
                raise UnsupportedDirective(name)
Directive.directives = {}

class AccountDirective(Directive):
    keyword = 'account'

    def __init__(self, account):
        self.account = account

