import os
import logging
import logging.config


def convert_value_to_int(value):
    try:
        return int(value)
    except TypeError:
        return 0


class ConfigurationError(Exception):
    pass


class Config:
    DEBUG = os.getenv('DEBUG')
    QUIZ_QUESTIONS_DIRECTORY = os.getenv('QUIZ_QUESTIONS_DIRECTORY')
    LOGS_DIRECTORY = os.getenv('LOGS_DIRECTORY')
    DEFAULT_ENCODING = 'KOI8-R'
    QUIZ_QUESTIONS_FILEPARSING_LIMIT = convert_value_to_int(
        os.getenv('QUIZ_QUESTIONS_FILEPARSING_LIMIT')
    )
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
    if DEBUG:
        REDIS_SETTINGS = {
            'host': os.getenv('REDIS_HOST'),
            'port': convert_value_to_int(os.getenv('REDIS_PORT')),
            'url': None
        }
    else:
        REDIS_SETTINGS = {
            'host': None,
            'port': None,
            'url': os.getenv('REDIS_URL')
        }

    required = [
        'DEBUG',
        'QUIZ_QUESTIONS_DIRECTORY',
        'LOGS_DIRECTORY',
        'DEFAULT_ENCODING',
        'QUIZ_QUESTIONS_FILEPARSING_LIMIT',
        'TELEGRAM_BOT_TOKEN',
        'VK_GROUP_TOKEN',
        'REDIS_SETTINGS',
    ]


def validate_config(config):
    errors = []
    for key in config.required:
        if not getattr(Config, key):
            errors.append(
                f'Environment variable {key} has not been configured properly.'
            )
    if errors:
        error_message = '\n'.join(errors)
        raise ConfigurationError(error_message)


def setup_logging():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s — %(name)s — %(levelname)s — %(message)s'
            }
        },
        'handlers': {
            'console': {'class': 'logging.StreamHandler', 'formatter': 'standard'},
        },
        'loggers': {
            '': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True}
        },
    }

    logging.config.dictConfig(logging_config)
