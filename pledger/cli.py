from argparse import ArgumentParser
from .account import Account
from .report import reports
from .filter import Filter, BeginFilter, EndFilter
from .pattern import PatternParser
from .parser import Parser
from .sorting import MapSorting, ExpressionSorting
from .rule import RuleCollection
from .template import default_template
from ._version import __version__
import re
import os
import sys

parser = Parser()
filter = Filter.null
rules = RuleCollection()
sorting = MapSorting(lambda x: x.date)


def run_cli():
    global filter
    global sorting

    argparser = ArgumentParser()
    argparser.add_argument("report", action="store")
    argparser.add_argument("--version", action="version", version=__version__)
    argparser.add_argument("--filename", "-f", action="append", type=str)
    for flag in Filter.flags:
        argparser.add_argument("--%s" % flag.name, nargs=flag.args)
    argparser.add_argument("--sort", nargs=1)
    argparser.add_argument("--sortb", nargs=1)
    argparser.add_argument("patterns", metavar="PATTERN", type=str, nargs="*")

    args = argparser.parse_args()

    report_factory = reports.get(args.report)
    if report_factory is None:
        raise Exception("no such report " + args.report)
    if args.patterns:
        pattern_parser = PatternParser(args.patterns)
        filter &= pattern_parser.parse_filter()

    filenames = args.filename
    if filenames is None:
        path = os.environ.get("PLEDGER")
        if path:
            filenames = [path]

    if filenames is None:
        sys.stderr.write("No ledger specified\n")
        sys.exit(1)

    ledgers = [parser.parse_ledger(path) for path in filenames]

    for flag in Filter.flags:
        parameters = getattr(args, flag.name)
        if parameters:
            f = flag.filter.parse(parser, *parameters)
            if f:
                filter &= f

    if args.sort:
        sorting = ExpressionSorting(parser, *args.sort)
    elif args.sortb:
        sorting = ~ExpressionSorting(parser, *args.sortb)

    report = report_factory(parser, rules, filter, sorting)
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 200
    template = default_template
    return template(width, ledgers, report, print)
