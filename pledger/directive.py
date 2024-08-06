class DirectiveMetaclass(type):
    def __new__(cls, name, bases, attrs):
        result = super(DirectiveMetaclass, cls).__new__(cls, name, bases, attrs)
        if name != "Directive":
            Directive.directives[attrs["keyword"]] = result
        return result


class UnsupportedDirective(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Directive(object, metaclass=DirectiveMetaclass):
    pass


Directive.directives = {}


class AccountDirective(Directive):
    keyword = "account"

    def __init__(self, account):
        self.account = account

    def execute(self, processor):
        processor.add_account_prefix(self.account)


class IncludeDirective(Directive):
    keyword = "include"

    def __init__(self, filename):
        self.filename = filename

    def execute(self, processor):
        processor.include(self.filename)


class EndAccountDirective(Directive):
    keyword = "end"

    def execute(self, processor):
        processor.remove_account_prefix()
