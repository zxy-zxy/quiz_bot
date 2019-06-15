import logging
from collections import Iterable
import json
import dataclasses

import redis

logger = logging.getLogger(__name__)


class RedisStorage:
    connection = None

    @staticmethod
    def initialize(host=None, port=None, url=None):
        logger.debug(
            'Redis instance initialization started, host: {}, port: {}, url: {}'.format(
                host, port, url
            )
        )
        if url:
            RedisStorage.connection = redis.Redis.from_url(url)
        else:
            RedisStorage.connection = redis.Redis(host, port)

    @staticmethod
    def add_records_to_set(set_name, records):
        if not isinstance(records, Iterable):
            records = [records]
        dumped_records = [json.dumps(dataclasses.asdict(record)) for record in records]
        return RedisStorage.connection.sadd(set_name, *dumped_records)

    @staticmethod
    def get_random_record_from_set(set_name):
        random_record = RedisStorage.connection.srandmember(set_name)
        random_record_dict = json.loads(random_record)
        return random_record_dict

    @staticmethod
    def set(key, value):
        return RedisStorage.connection.set(key, value)

    @staticmethod
    def get(key):
        value = RedisStorage.connection.get(key)
        value = value if value is None else value.decode()
        return value

    @staticmethod
    def increase_value(key, value=1):
        return RedisStorage.connection.incr(key, value)
