# core/database.py

import asyncio
from .in_memory_database import InMemoryDatabase
from .database_channel import DatabaseChannel

class Database:
    def __init__(self, discord_client, config):
        self._discord_client = discord_client
        self._config = config
        self._lock = asyncio.Lock()
        self._in_memory_database = None
        self._database_channel = DatabaseChannel(self._discord_client, self._config)

    async def load(self):
        async with self._lock:
            records_from_db = await self._database_channel.load()
            self._in_memory_database = InMemoryDatabase()
            self._in_memory_database.load(records_from_db)

    async def get_channel_scanning_cursor(self, channel_id):
        async with self._lock:
            return self._in_memory_database.get_channel_scanning_cursor(channel_id)

    async def get_member_activity(self, user_id):
        async with self._lock:
            return self._in_memory_database.get_member_activity(user_id)

    async def upsert_record(self, record):
        async with self._lock:
            self._in_memory_database.upsert_record(record)

    async def flush_updates(self):
        async with self._lock:
            records = self._in_memory_database.flush_updated_records()
            for record in records:
                await self._database_channel.upsert_record(record)
            return len(records)
