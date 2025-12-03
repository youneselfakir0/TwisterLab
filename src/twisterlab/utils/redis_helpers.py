import json
import os

from redis import Redis


class RedisHelper:
    def __init__(self, host=None, port=None, db=0):
        self.redis = Redis(
            host=host or os.getenv("REDIS_HOST", "localhost"),
            port=port or int(os.getenv("REDIS_PORT", 6379)),
            db=db,
        )

    def set(self, key, value, expire=None):
        if isinstance(value, dict):
            value = json.dumps(value)
        self.redis.set(key, value, ex=expire)

    def get(self, key):
        value = self.redis.get(key)
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    def delete(self, key):
        return self.redis.delete(key)

    def exists(self, key):
        return self.redis.exists(key) > 0

    def keys(self, pattern="*"):
        return self.redis.keys(pattern)

    def flushdb(self):
        return self.redis.flushdb()
