from pathlib import Path

import redis

from seeder.core import Seeder


class RedisSeeder(Seeder):
    def __init__(self, host: str, port: int):
        self._client = redis.Redis(host=host, port=port)

    def truncate(self) -> None:
        self._client.flushall(asynchronous=False)

    def seed(self, folder: Path) -> None:
        pass
