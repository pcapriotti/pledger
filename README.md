# Introduction

pledger is a collection of utilities for tracking money with python according to standard accounting principles.

It is inspired by John Wiegley's ledger, and most ledger input files should work with pledger without modifications.

# For ledger users

If you are a ledger user, you can just run

    export PLEDGER=$LEDGER
    python main.py reg

and you are pretty much ready to go. Note, however, that rules inside ledger files are ignored, so they need to be translated into python and added to your startup script (see below).

pledger has nowhere near as many command line options as ledger, but much of the functionality can be recreated by clever uses of the --filter option.

## Getting started

pledger is based on three simple concepts: accounts, transactions and entries.

Accounts represent ideal containers for money, often abstract. Examples of accounts include a bank account, rent expenses, and a credit card debt. Accounts in ledger can be organized in a hierarchy, by using a colon (:) as a separator for subaccounts (e.g. Assets:Bank:Checking and Assets:Bank:Savings).

Money flows from an account to another through transactions, leaving the total amount of money in the whole system constant. A transaction is composed by entries (usually 2) which describe the individual changes in each of the accounts involved.

For example, paying your 1000 € rent with a bank transfer can be represented as a transaction with two entries: one taking 1000 € out of your checking account, and one adding 1000 € into the account tracking rent expenses.

Since transactions cannot ever create or destroy money, the sum of the amounts of all the entries of a transaction should always be 0.

Transactions can be written in text files which pledger is able to parse using a syntax such as in the following example:

    2011/07/01 * Rent
        Assets:Bank             -1000.00 €
        Expenses:Rent

As you can see, this expression includes the date of the transaction, an optional * mark representing whether the trasaction is "cleared" (which means whatever you want it to mean, but usually, that you have verified the transaction on a bank statement), and an arbitrary label that describes it.

After that, there is a list of entries, written as <account> <2 or more spaces> <amount>. One of the amounts can be omitted, since it is implied that is equal to the opposite of the sum of the others (remember each transaction has to total 0).

A pledger input file can contain a list of transactions separated by a blank line.

## Reports

There are two types of reports that pledger is natively able to generate (although pledger can be easily extended to allow other types of reports).

Both reports allow the use of filters to restrict which entries and transactions should be taken into account.

### Balance report

A balance report lists all accounts and their respective total, assuming it is non-zero. Account names are shown indented according to their hierarchy. For example:

    pledger balance Assets:Bank

would show something like:

    2910.12 €  Assets:Bank
     615.12 €    Checking
    2295.00 €    Savings

### Register report

A register report simply lists all entries matching the given filter, with a running total.

## Filters

Filters are functions that take a transaction and one of its entries, and return a boolean value which indicates whether the entry has to be included in the report being generated.

Filters can be either created in python code, or specified in the command line using python syntax. For example, a command like the following:

    pledger register --filter "transaction.label.contains('Rent')"

will list all entries containing the string "Rent" in their description.

Simpler filters can be specified in the command line. Run

    pledger --help

for a complete list.

## Rules

A rule consists of a filter, together with a function, called generator, which takes a single entry and returns a list (or an iterator) of entries. Think of a rule as a transformation to be applied to certain entries.

## Startup scripts

pledger's command line interface can be invoked by importing the `cli` module and executing

    cli.run_cli()

The `cli` module also contains a number of global variables that can be used to customize pledger's behavior.

For example, setting `cli.filter` allows to specify a predefined filter that is composed with whatever filter is provided on the command line. Rules can be added to the global `cli.rules`.

A startup script allows you to define new report types, or custom representations for existing reports.

## Tags

Entries, transactions and accounts can have tags attached to them. A tag is an arbitrary key-value pair. Some tags are reversed, and have a special meaning to pledger, like the 'date' tag for an entry, which changes its date.

Tags for entries and transactions can be specified in the input file, but account tags can only be set in python code at the moment.

For transactions, a comment after the first line can contain tags written as tag:value, or simply :tag:, in which case the value is assumed to be the True. A date enclosed in square brackets is considered to be a date tag with the specified value. Entry tags have the same syntax, but come after the entry on the same line.

And example is

    2011/07/01 * Rent
    ; landlord:Smith
        Expenses:Rent               1000 €      ; [2011/07/03]
        Assets:Bank                             ; :direct-debit:

which should be pretty self-explanatory.

To set tags on accounts in your startup script, use code such as the following

    accounts = cli.parser.accounts
    accounts["Assets"]["Bank"].tags["checking"] = True

When filtering on the command line, you can access tags as though they were properties of an object. For example:

    pledger balance --filter 'entry.account.checking'

    pledger register Expenses:Rent --filter 'transaction.landlord == "Smith"'
