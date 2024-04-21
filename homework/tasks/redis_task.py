import redis.asyncio as aredis


class UsersByTitleStorage:
    def __init__(self):
        self._client = aredis.StrictRedis()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        await self._client.aclose()

    async def save_item(self, user_id: int, title: str) -> None:

        await self._client.sadd(title, user_id)

    async def find_users_by_title(self, title: str) -> list[int]:

        return [int(user_id) for user_id in await self._client.smembers(title)]
