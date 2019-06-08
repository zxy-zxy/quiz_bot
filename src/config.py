import os
import logging
import logging.config


def convert_value_to_int(value):
    try:
        return int(value)
    except TypeError:
        return 0


class ConfigError(Exception):
    pass


class Config:
    DEBUG = True
    QUIZ_QUESTIONS_DIRECTORY = os.getenv('QUIZ_QUESTIONS_DIRECTORY')
    DEFAULT_ENCODING = 'KOI8-R'
    QUIZ_QUESTIONS_FILEPARSING_LIMIT = convert_value_to_int(
        os.getenv('QUIZ_QUESTIONS_FILEPARSING_LIMIT')
    )
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')

    required = [
        'QUIZ_QUESTIONS_DIRECTORY',
        'DEFAULT_ENCODING',
        'QUIZ_QUESTIONS_FILEPARSING_LIMIT',
        'TELEGRAM_BOT_TOKEN',
        'VK_GROUP_TOKEN',
        'REDIS_SETTINGS',
    ]


class DevelopmentConfig(Config):
    REDIS_SETTINGS = {
        'host': os.getenv('REDIS_HOST'),
        'port': convert_value_to_int(os.getenv('REDIS_PORT')),
        'url': None,
    }


class ProductionConfig(Config):
    DEBUG = False
    REDIS_SETTINGS = {'host': None, 'port': None, 'url': os.getenv('REDIS_URL')}


def validate_config(config):
    errors = []
    for key in config.required:
        if not getattr(config, key):
            errors.append(
                f'Environment variable {key} has not been configured properly.'
            )
    if errors:
        error_message = '\n'.join(errors)
        raise ConfigError(error_message)


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
            'console': {'class': 'logging.StreamHandler', 'formatter': 'standard'}
        },
        'loggers': {'': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True}},
    }

    logging.config.dictConfig(logging_config)
