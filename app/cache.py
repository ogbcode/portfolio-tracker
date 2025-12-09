"""Redis cache connection and utilities."""

import json
from typing import Any, Optional

import redis.asyncio as redis

from app.config import get_settings


class Cache:
    """Redis cache manager."""
    
    client: redis.Redis = None
    
    async def connect(self) -> None:
        """Establish connection to Redis."""
        settings = get_settings()
        self.client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if not self.client:
            return None
        
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache with optional TTL."""
        if not self.client:
            return
        
        settings = get_settings()
        ttl = ttl or settings.redis_ttl_seconds
        
        await self.client.set(key, json.dumps(value), ex=ttl)
    
    async def delete(self, key: str) -> None:
        """Remove value from cache."""
        if self.client:
            await self.client.delete(key)


cache = Cache()
