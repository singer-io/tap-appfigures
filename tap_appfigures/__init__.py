"""
tap_appfigures package

Singer tap for the AppFigures API
Singer: https://github.com/singer-io/getting-started
AppFigures API: https://docs.appfigures.com/
"""

import argparse

import singer

import tap_appfigures.client
import tap_appfigures.streams
from tap_appfigures.runner import AppFiguresRunner
from tap_appfigures.state import State

LOGGER = singer.get_logger()


def parse_args(required_config_keys):
    """
    Parse standard command-line args.

    Copied, and then adapted, from singer-python.utils

    Parses the command-line arguments mentioned in the SPEC and the
    BEST_PRACTICES documents:

    -c,--config     Config file
    -s,--state      State file
    -d,--discover   Run in discover mode
    -p,--properties Properties file: DEPRECATED, please use --catalog instead
    --catalog       Catalog file

    Returns the parsed args object from argparse. For each argument that
    point to JSON files (config, state, properties), we will automatically
    load and parse the JSON file.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help='Config file',
        required=True)

    parser.add_argument(
        '-s', '--state',
        help='State file')

    parser.add_argument(
        '--catalog',
        help='Catalog file')

    parser.add_argument(
        '-d', '--discover',
        action='store_true',
        help='Do schema discovery')

    args = parser.parse_args()
    if args.config:
        args.config = singer.load_json(args.config)
    if args.catalog:
        args.catalog = singer.catalog.Catalog.load(args.catalog)

    singer.utils.check_config(args.config, required_config_keys)

    return args


@singer.utils.handle_top_exception(LOGGER)
def main():
    """
    Main function - process args, build runner, execute request
    """
    args = parse_args(
        required_config_keys=['api_key', 'username', 'password', 'start_date'])

    runner = AppFiguresRunner(
        client=tap_appfigures.client.AppFiguresClient(args.config),
        state=State(args.state),
        catalog=args.catalog
    )

    if args.discover:
        runner.do_discover()
    else:
        runner.do_sync()


if __name__ == '__main__':
    main()
