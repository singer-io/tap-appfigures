"""
tap_appfigures package

Singer tap for the AppFigures API
Singer: https://github.com/singer-io/getting-started
AppFigures API: https://docs.appfigures.com/
"""

import singer

import tap_appfigures.client
import tap_appfigures.streams
from tap_appfigures.runner import AppFiguresRunner

LOGGER = singer.get_logger()


@singer.utils.handle_top_exception(LOGGER)
def main():
    """
    Main function - process args, build runner, execute request
    """
    args = singer.utils.parse_args(
        required_config_keys=['api_key', 'username', 'password', 'start_date']
    )

    runner = AppFiguresRunner(
        client=tap_appfigures.client.AppFiguresClient(args.config),
        state=args.state,
        catalog=args.catalog
    )

    if args.discover:
        runner.do_discover()
    else:
        runner.do_sync()


if __name__ == '__main__':
    main()
