import os
import logging
import threading
from redis import Redis, ConnectionPool, exceptions
from cachetools import TTLCache

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("robust_redis")

# ---------- CONFIG ----------
redis_url = os.getenv('REDIS_DB', 'redis://localhost:6379/0')

# ---------- REDIS CONNECTION POOL ----------
pool = ConnectionPool.from_url(
    redis_url,
    max_connections=50,
    socket_connect_timeout=2,
    socket_timeout=2
)

# ---------- REDIS CLIENT ----------
_primary_redis = Redis(connection_pool=pool)

# ---------- FALLBACK TTL CACHE (in-memory) ----------
_fallback_cache = TTLCache(maxsize=1000, ttl=300)
_fallback_lock = threading.Lock()

# ---------- WRAPPER CLASS ----------
class RobustRedisClient:
    def __init__(self, primary, fallback_cache):
        self.redis = primary
        self.fallback = fallback_cache

    def get(self, key, decode=True):
        try:
            value = self.redis.get(key)
            if value is not None:
                return value.decode() if decode and isinstance(value, bytes) else value
            raise exceptions.RedisError("Key not found in Redis")
        except exceptions.RedisError as e:
            logger.warning(f"[Redis GET] {e}")
            with _fallback_lock:
                value = self.fallback.get(key, None)
                return value.decode() if decode and isinstance(value, bytes) else value

    def set(self, key, value, ex=None):
        try:
            self.redis.set(key, value, ex=ex)
        except exceptions.RedisError as e:
            logger.warning(f"[Redis SET] {e}")
            with _fallback_lock:
                self.fallback[key] = value

    def setex(self, key, time, value):
        """Support libraries expecting setex."""
        try:
            self.redis.set(key, value, ex=time)
        except exceptions.RedisError as e:
            logger.warning(f"[Redis SETEX] {e}")
            with _fallback_lock:
                self.fallback[key] = value

    def delete(self, key):
        try:
            self.redis.delete(key)
        except exceptions.RedisError as e:
            logger.warning(f"[Redis DELETE] {e}")
            with _fallback_lock:
                self.fallback.pop(key, None)

    def exists(self, key):
        try:
            return self.redis.exists(key)
        except exceptions.RedisError as e:
            logger.warning(f"[Redis EXISTS] {e}")
            with _fallback_lock:
                return key in self.fallback

    def flush_fallback(self):
        with _fallback_lock:
            self.fallback.clear()

# ---------- SINGLETON INSTANCE ----------
redis_client = RobustRedisClient(_primary_redis, _fallback_cache)