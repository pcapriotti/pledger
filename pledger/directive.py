class DirectiveMetaclass(type):
    def __new__(cls, name, bases, attrs):
        result = super(DirectiveMetaclass, cls).__new__(cls, name, bases, attrs)
        if name != "Directive":
            Directive.directives[attrs['keyword']] = result
        return result

class UnsupportedDirective(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Directive(object):
    __metaclass__ = DirectiveMetaclass

    @classmethod
    def parse(cls, str):
        if str[0] == '!':
            args = str[1:].split(' ')
            name = args[0]
            args = args[1:]
            directive_class = cls.directives.get(name)
            if directive_class:
                return directive_class(*args)
            else:
                raise UnsupportedDirective(name)
Directive.directives = {}

class AccountDirective(Directive):
    keyword = 'account'

    def __init__(self, account):
        self.account = account

    def execute(self, processor):
        processor.add_account_prefix(self.account)

class IncludeDirective(Directive):
    keyword = 'include'

    def __init__(self, filename):
        self.filename = filename

    def execute(self, processor):
        """not implemented"""
