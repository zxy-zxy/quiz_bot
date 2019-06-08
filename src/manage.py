import sys
import argparse
import logging
import os

from application.common.database import RedisStorage
from config import (
    ProductionConfig,
    DevelopmentConfig,
    setup_logging,
    validate_config,
    ConfigError,
)

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
    application_environment = os.getenv('APPLICATION_ENV')

    if application_environment == 'development':
        application_config = DevelopmentConfig
    elif application_environment == 'production':
        application_config = ProductionConfig
    else:
        sys.stdout.write(
            'Application environment setup required: env APPLICATION_ENV should be'
            'development or production'
        )
        sys.exit(1)

    try:
        validate_config(application_config)
    except ConfigError as e:
        sys.stdout.write(str(e))
        sys.exit(1)

    setup_logging()

    RedisStorage.initialize(**application_config.REDIS_SETTINGS)

    arg_parser = create_parser()
    args = arg_parser.parse_args()

    if args.command == 'populate_db':
        populate_db.run_command(
            application_config.QUIZ_QUESTIONS_DIRECTORY,
            application_config.DEFAULT_ENCODING,
            application_config.QUIZ_QUESTIONS_FILEPARSING_LIMIT,
        )
    elif args.command == 'run':
        if args.platform == 'telegram':
            run_telegram_bot.run_command(application_config.TELEGRAM_BOT_TOKEN)
        elif args.platform == 'vk':
            run_vk_bot.run_command(application_config.VK_GROUP_TOKEN)
        else:
            sys.stdout.write('Unknown command. Please refer for help.')
            sys.exit(1)

    else:
        sys.stdout.write('Unknown command. Please refer for help.')
        sys.exit(1)


if __name__ == '__main__':
    main()
