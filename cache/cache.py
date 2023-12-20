import json
import typing

import redis

import settings

_redis_cache = redis.Redis(
    host=settings.Redis.host,
    port=settings.Redis.port,
    # password=settings.Redis.password,
    db=settings.Redis.db_cache
)


def redis_cache(ttl: int = settings.Redis.ttl):
    def decorator(function: typing.Callable):
        def wrapper(*args, **kwargs):
            key = f'{function.__name__}_{hash(args)}_{hash(frozenset(kwargs.items()))}'
            result = _redis_cache.get(key)
            if result is None:
                value = function(*args, **kwargs)
                value_json = json.dumps(value)
                _redis_cache.set(name=key, value=value_json, ex=ttl)
            else:
                value_json = result.decode('utf-8')
                value = json.loads(value_json)
            return value

        return wrapper

    return decorator
