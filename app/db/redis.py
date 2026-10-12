import redis.asyncio as redis
from core.settings import settings


class RedisClient:
    def __init__(self, host: str, port: int, db: int = 0):
        self.pool: redis.ConnectionPool = redis.ConnectionPool(
            host=host, port=port, db=db
        )

    async def get_redis_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.pool)


redis_client = RedisClient(host=settings.redis.HOST, port=settings.redis.PORT)
