"""Redis caching service for performance optimization."""
import json
import redis
from typing import Any, Optional
from ..config import settings


class CacheService:
    """Service for managing Redis cache."""

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            # Log error and return None to fall back to database
            print(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set value in cache with TTL (time to live).

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 5 minutes)
        """
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)  # default=str handles datetime
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Cache set error: {e}")

    def delete(self, key: str):
        """Delete key from cache."""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")

    def delete_pattern(self, pattern: str):
        """Delete all keys matching a pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache delete pattern error: {e}")

    def get_or_set(self, key: str, getter_fn, ttl: int = 300) -> Any:
        """
        Get from cache or execute function and cache result.

        Args:
            key: Cache key
            getter_fn: Function to execute if cache miss
            ttl: Time to live in seconds

        Returns:
            Cached or fresh value
        """
        # Try to get from cache
        cached = self.get(key)
        if cached is not None:
            return cached

        # Cache miss - get fresh data
        value = getter_fn()

        # Cache the result
        if value is not None:
            self.set(key, value, ttl)

        return value


# Global cache instance
cache = CacheService()


# Helper functions for specific caching patterns

def cache_user_quota(user_id: str, quota_data: dict, ttl: int = 60):
    """Cache user quota data (1 minute TTL since it changes frequently)."""
    cache.set(f"quota:{user_id}", quota_data, ttl)


def get_cached_user_quota(user_id: str) -> Optional[dict]:
    """Get cached user quota data."""
    return cache.get(f"quota:{user_id}")


def invalidate_user_quota(user_id: str):
    """Invalidate cached user quota."""
    cache.delete(f"quota:{user_id}")


def cache_admin_stats(stats_data: dict, ttl: int = 300):
    """Cache admin stats (5 minutes TTL)."""
    cache.set("admin:stats", stats_data, ttl)


def get_cached_admin_stats() -> Optional[dict]:
    """Get cached admin stats."""
    return cache.get("admin:stats")


def invalidate_admin_stats():
    """Invalidate cached admin stats."""
    cache.delete("admin:stats")


def cache_mood_details(mood_id: str, mood_data: dict, ttl: int = 600):
    """Cache mood details (10 minutes TTL)."""
    cache.set(f"mood:{mood_id}", mood_data, ttl)


def get_cached_mood(mood_id: str) -> Optional[dict]:
    """Get cached mood details."""
    return cache.get(f"mood:{mood_id}")


def invalidate_mood(mood_id: str):
    """Invalidate cached mood."""
    cache.delete(f"mood:{mood_id}")


def invalidate_all_moods():
    """Invalidate all cached moods."""
    cache.delete_pattern("mood:*")
