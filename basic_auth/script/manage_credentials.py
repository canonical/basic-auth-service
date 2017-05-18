"""Manage basic-auth credentials for API access."""

import sys
import argparse

import prettytable

import uvloop

import psycopg2

from aiopg.sa import create_engine

from ..config import load_config
from ..credential import generate_random_token
from ..db import run_in_transaction
from ..db.model import APICredentials


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--config', help='Configuration file', type=argparse.FileType(),
        default='config.yaml')
    subparsers = parser.add_subparsers(
        help='The action to perform', dest='action', metavar='action')
    subparsers.required = True

    add_parser = subparsers.add_parser('add', help='Add credentials')
    add_parser.add_argument('username', help='Credentials username')
    add_parser.add_argument('--description', help='User description')

    remove_parser = subparsers.add_parser('remove', help='Remove credentials')
    remove_parser.add_argument('username', help='Username to remove')

    subparsers.add_parser('list', help='List credentials')
    return parser.parse_args(args=args)


async def call_model_method(loop, dsn, method, *args, **kwargs):
    """Call the specified Model method with arguments."""
    async with create_engine(dsn=dsn, loop=loop) as engine:
        return await run_in_transaction(engine, method, *args, **kwargs)


def db_call(args, config, loop=None):
    """Make the appropriate DB query."""
    if loop is None:
        loop = uvloop.new_event_loop()  # pragma: no cover

    method_args = ()
    if args.action == 'add':
        method = 'add_api_credentials'
        password = generate_random_token()
        method_args = (args.username, password, args.description)
    elif args.action == 'remove':
        method = 'remove_api_credentials'
        method_args = (args.username,)
    else:  # list action
        method = 'get_all_api_credentials'

    return loop.run_until_complete(
        call_model_method(
            loop, config['db', 'dsn'], method, *method_args))


def print_result(result, file=sys.stdout):
    """Print result from model call."""
    if isinstance(result, bool):
        if not result:
            print('No action performed', file=file)
        return

    if not isinstance(result, list):
        result = [result]

    table = prettytable.PrettyTable(
        field_names=APICredentials._fields,
        header_style='cap')
    table.align = 'l'

    for row in result:
        table.add_row(row)
    print(table, file=file)


def main(loop=None, raw_args=None, file=sys.stdout):
    """Script main."""
    args = parse_args(args=raw_args)
    config = load_config(args)
    try:
        result = db_call(args, config, loop=loop)
    except psycopg2.IntegrityError:
        sys.exit('The specified username already exists')
    print_result(result, file=file)
