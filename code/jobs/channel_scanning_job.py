# jobs/channel_scanning_job.py

import asyncio

from models.database.channel_scanning_cursor import ChannelScanningCursor
from models.database.member_activity import MemberActivityRecord, MemberActivityStatus

class ChannelScanningJob:

    def __init__(self, discord_client, database, config):
        self._discord_client = discord_client
        self._database = database
        self._config = config

    async def run(self):
        print("Scan Job started")
        while True:
            await self.scan_all_channels()
            await asyncio.sleep(self._config.channel_scanning_config.minutes_between_scans * 60)

    async def scan_all_channels(self):
        # TODO: scan all channels visible to the bot.
        for channel_pruning_config in self._config.channel_pruning_configs:
            await self.process_new_messages_in_channel(channel_pruning_config.channel_id)

    async def process_new_messages_in_channel(self, channel_id):
        cursor = await self._database.get_channel_scanning_cursor(channel_id)
        messages, updated_cursor = await self._scan_channel_from_cursor(channel_id, cursor)

        print("Calculated new cursor: " + str(updated_cursor))
        db_updates = [] if updated_cursor is None else [updated_cursor]
        db_updates += self._process_messages(messages)

        for update in db_updates:
            self._database.queue_update(update)
        await self._database.commit_updates()

        print("Committed updates to database.")

    async def _scan_channel_from_cursor(self, channel_id, cursor):
        channel = self._discord_client.get_channel(channel_id)
        if not channel:
            raise ValueError(f"Our bot does not have access to channel_id={channel_id}")

        if cursor is not None:
            raise NotImplemented("scanning from cursor")

        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            messages.append(message)

        category = f"{channel.category.name}: " if channel.category else ""
        print(f"Finished scanning {category}{channel.name} ({channel.id}) for new messages. Found {len(messages)} messages.")

        updated_cursor = self._create_updated_cursor(cursor, messages)
        return messages, updated_cursor

    def _process_messages(self, messages):
        member_activity_records = self._convert_to_member_activity_records(messages)
        print("Calculated member activity records:")
        for record in member_activity_records:
            print(record)

        db_updates = member_activity_records
        return db_updates

    def _convert_to_member_activity_records(self, messages):
        record_by_user_id = dict()

        for message in messages:
            uid = message.author.id
            if uid in record_by_user_id:
                record = record_by_user_id[uid].replace_with_latest_message(message)
            else:
                record = MemberActivityRecord.create_from_message(message)
            record_by_user_id[uid] = record

        return list(record_by_user_id.values())

    def _create_updated_cursor(self, old_cursor, messages):
        if old_cursor is None:
            return ChannelScanningCursor.create_from_latest_messages(messages)
        else:
            return old_cursor.replace_with_latest_messages(messages)
