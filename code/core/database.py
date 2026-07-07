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
            self._in_memory_database = InMemoryDatabase(records_from_db)

    async def get_channel_scanning_cursor(self, channel_id):
        async with self._lock:
            return self._in_memory_database.get_channel_scanning_cursor(channel_id)

    async def get_member_activity(self, user_id):
        async with self._lock:
            return self._in_memory_database.get_member_activity(user_id)

    def queue_update(self, record):
        # TODO
        pass

    async def commit_updates(self):
        async with self._lock:
            # TODO: commit queued updates to #bot-database channel and update in memory db
            pass
