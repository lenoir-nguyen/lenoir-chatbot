"""
Cache management using Redis for session data storage.

This module provides a simple, reusable interface for caching short-lived data
(user sessions, preferences, etc.) using Redis. It gracefully handles connection
errors, allowing the application to function even if Redis is unavailable.

Redis is used as an optional optimization layer:
- Fast retrieval of user preferences (language, theme, etc.)
- Reduces repeated database queries
- Data automatically expires after TTL (Time To Live)

Note: If Redis is unavailable, operations fail silently. The application
continues to work with fallback logic (e.g., using request parameters).
"""

import os
import json
import redis
from typing import Optional, Any

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(redis_url, decode_responses=True)


async def cache_get(key: str) -> Optional[dict]:
    """
    Retrieve cached data from Redis.

    This function attempts to fetch a cached value by key. If the key exists,
    it deserializes the JSON string back into a Python dictionary. If Redis
    is unavailable or the key doesn't exist, it returns None.

    Args:
        key (str): The cache key to retrieve (e.g., "session:user123")

    Returns:
        Optional[dict]: Deserialized cached data, or None if not found

    Example:
        >>> session = await cache_get("session:user123")
        >>> if session:
        ...     language = session.get("language", "en")
    """
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except (redis.ConnectionError, json.JSONDecodeError):
        return None


async def cache_set(key: str, value: dict, ttl: int = 3600) -> None:
    """
    Store data in Redis with automatic expiration.

    This function serializes a dictionary to JSON and stores it in Redis with
    a specified Time To Live (TTL). After TTL seconds, Redis automatically
    deletes the key. If Redis is unavailable, the operation fails silently.

    Args:
        key (str): The cache key to store under (e.g., "session:user123")
        value (dict): Dictionary data to cache
        ttl (int): Time To Live in seconds (default: 3600 = 1 hour)

    Returns:
        None

    Example:
        >>> session_data = {"language": "en", "user_id": "123"}
        >>> await cache_set("session:user123", session_data, ttl=86400)
    """
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except redis.ConnectionError:
        pass


async def cache_delete(key: str) -> None:
    """
    Remove a key from Redis cache.

    This function deletes a key from Redis immediately. If the key doesn't
    exist, no error is raised. If Redis is unavailable, the operation fails silently.

    Args:
        key (str): The cache key to delete (e.g., "session:user123")

    Returns:
        None

    Example:
        >>> await cache_delete("session:user123")
    """
    try:
        redis_client.delete(key)
    except redis.ConnectionError:
        pass


def is_redis_available() -> bool:
    """
    Check if Redis server is running and accessible.

    This function sends a PING command to Redis. If Redis responds, the
    connection is working. This is useful for health checks and determining
    whether to enable caching-dependent features.

    Returns:
        bool: True if Redis is accessible, False otherwise

    Example:
        >>> if is_redis_available():
        ...     print("Cache is enabled")
        ... else:
        ...     print("Running without cache")
    """
    try:
        redis_client.ping()
        return True
    except (redis.ConnectionError, Exception):
        return False
