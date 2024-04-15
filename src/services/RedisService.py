from redis import Redis

from src.celery import app as celery


class RedisService(object):
    def __init__(self):
        self.celery = celery

    async def get_status(self, task_id: str):
        task = self.celery.AsyncResult(task_id)
        return task.state

    async def set(self, key: str, value: str, expire: int = 0):
        await self.redis.set(key, value, expire)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)
