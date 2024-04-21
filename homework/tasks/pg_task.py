from dataclasses import dataclass

import asyncpg


@dataclass
class ItemEntry:
    item_id: int
    user_id: int
    title: str
    description: str


class ItemStorage:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        # We initialize client here, because we need to connect it,
        # __init__ method doesn't support awaits.
        #
        # Pool will be configured using env variables.
        self._pool = await asyncpg.create_pool()

    async def disconnect(self) -> None:
        # Connections should be gracefully closed on app exit to avoid
        # resource leaks.
        await self._pool.close()

    async def create_tables_structure(self) -> None:

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    item_id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    CONSTRAINT unique_item UNIQUE (user_id, title, description)
                )
                """
            )

    async def save_items(self, items: list[ItemEntry]) -> None:

        async with self._pool.acquire() as conn:
            values = [
                (item.item_id, item.user_id, item.title, item.description) for
                item in items]
            await conn.executemany(
                """
                INSERT INTO items (item_id, user_id, title, description)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (item_id) DO NOTHING
                """,
                values
            )

    async def find_similar_items(
            self, user_id: int, title: str, description: str
    ) -> list[ItemEntry]:

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM items
                WHERE user_id = $1 AND title = $2 AND description = $3
                """,
                user_id, title, description
            )
            return [ItemEntry(**row) for row in rows]
