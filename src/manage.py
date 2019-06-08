import sys
import argparse
import logging

from application.common.database import RedisStorage
from config import Config, setup_logging, validate_config, ConfigurationError

from application.commands import populate_db, run_vk_bot, run_telegram_bot

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('populate_db', help=populate_db.run_command.__doc__)

    run_parser = subparsers.add_parser('run')

    run_parser.add_argument(
        '--platform', type=str, help='Run bot on telegram or vk platform.'
    )

    return parser


def main():

    try:
        validate_config(Config)
    except ConfigurationError as e:
        sys.stdout.write(str(e))
        sys.exit(1)

    setup_logging()

    RedisStorage.initialize(**Config.REDIS_SETTINGS)

    arg_parser = create_parser()
    args = arg_parser.parse_args()

    if args.command == 'populate_db':
        populate_db.run_command()
    elif args.command == 'run':
        if args.platform == 'telegram':
            run_telegram_bot.run_command()
        elif args.platform == 'vk':
            run_vk_bot.run_command()
        else:
            sys.stdout.write('Unknown command. Please refer for help.')
            sys.exit(1)

    else:
        sys.stdout.write('Unknown command. Please refer for help.')
        sys.exit(1)


if __name__ == '__main__':
    main()
