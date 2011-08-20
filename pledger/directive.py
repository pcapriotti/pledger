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
        processor.include(self.filename)

class EndAccountDirective(Directive):
    keyword = 'end'

    def execute(self, processor):
        processor.remove_account_prefix()
