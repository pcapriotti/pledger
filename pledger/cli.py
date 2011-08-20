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

from argparse import ArgumentParser
from pledger.account import Account
from pledger.report import reports
from pledger.filter import Filter, BeginFilter, EndFilter
from pledger.pattern import PatternParser
from pledger.parser import Parser
from pledger.sorting import MapSorting, ExpressionSorting
from pledger.rule import RuleCollection
from pledger.template import default_template
import re, os, sys

parser = Parser()
filter = Filter.null
rules = RuleCollection()
transaction_rules = []
sorting = MapSorting(lambda x: x.date)
template = default_template

def output(line):
    print line.encode("utf-8")

def run_cli():
    global filter
    global sorting

    argparser = ArgumentParser()
    argparser.add_argument("report", action="store")
    argparser.add_argument("--filename", action="store", nargs=1)
    for flag in Filter.flags:
        argparser.add_argument("--%s" % flag.name, nargs=flag.args)
    argparser.add_argument("--sort", nargs=1)
    argparser.add_argument("--sortb", nargs=1)
    argparser.add_argument("patterns", metavar="PATTERN", type=str,
                           nargs="*")

    args = argparser.parse_args()

    report_factory = reports.get(args.report)
    if report_factory is None:
        raise Exception("no such report " + args.report)
    if args.patterns:
        pattern_parser = PatternParser(args.patterns)
        filter &= pattern_parser.parse_filter()

    filename = args.filename and args.filename[0] or None
    if filename is None:
        filename = os.environ.get("PLEDGER")

    if filename is None:
        sys.stderr.write("No ledger specified\n")
        sys.exit(1)

    ledger = parser.parse_ledger(filename)

    for flag in Filter.flags:
        parameters = getattr(args, flag.name)
        if parameters:
            f = flag.filter.parse(parser, *parameters)
            if f: filter &= f

    if args.sort:
        sorting = ExpressionSorting(parser, *args.sort)
    elif args.sortb:
        sorting = ~ExpressionSorting(parser, *args.sortb)

    report = report_factory(ledger, rules, transaction_rules, filter, sorting)
    return template(report, output)
