# core/database_channel.py

class DatabaseChannel:
    def __init__(self, discord_client):
        self._discord_client = discord_client

    async def read_database(self):
        pass

    async def upsert_record(self, record):
        pass

    def serialize_member_activity_record(self, record):
        pass

    def deserialize_member_activity_record(self, text):
        pass

    def serialize_channel_scanning_cursor(self, cursor):
        pass

    def deserialize_channel_scanning_cursor(self, text):
        pass
