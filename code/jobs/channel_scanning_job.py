# jobs/channel_scanning_job.py

import asyncio
import discord

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
        for channel in self._get_visible_channels():
            await self.process_new_messages_in_channel(channel.id)

    def _get_visible_channels(self):
        visible_channels = []

        for channel in self._discord_client.get_all_channels():
            if channel.guild.id != self._config.server_id:
                continue 
            if channel.id in [self._config.activity_db_channel_id, self._config.scanning_db_channel_id]:
                continue
            if not (isinstance(channel, discord.TextChannel) or \
                    isinstance(channel, discord.ForumChannel)):
                continue 

            permissions = channel.permissions_for(channel.guild.me)
            if permissions.read_messages:
                visible_channels.append(channel)

        return visible_channels

    async def process_new_messages_in_channel(self, channel_id):
        cursor = await self._database.get_channel_scanning_cursor(channel_id)
        messages = await self._scan_channel_from_cursor(channel_id, cursor)
        await self._process_messages(messages)
        await self._move_cursor(cursor, messages)
        update_count = await self._database.flush_updates()
        if update_count > 0:
            print("Committed updates to database.")
        else:
            print("No updates to commit.")

    async def _scan_channel_from_cursor(self, channel_id, cursor):
        channel = self._discord_client.get_channel(channel_id)
        if not channel:
            raise ValueError(f"Our bot does not have access to channel_id={channel_id}")

        if cursor is not None:
            after = discord.Object(id=cursor.last_scanned_message_id)
        else:
            after = None

        messages = []
        async for message in channel.history(limit=None, oldest_first=True, after=after):
            messages.append(message)

        category = f"{channel.category.name}: " if channel.category else ""
        print(f"Finished scanning {category}{channel.name} ({channel.id}) for new messages. Found {len(messages)} messages.")

        return messages

    async def _process_messages(self, messages):
        member_activity_records = self._convert_to_member_activity_records(messages)

        for record in member_activity_records:
            current_record = await self._database.get_member_activity(record.member_id)
            if current_record is None or current_record.last_seen_message_id < record.last_seen_message_id:
                await self._database.upsert_record(record)

    async def _move_cursor(self, old_cursor, messages):
        if old_cursor is None:
            updated_cursor = ChannelScanningCursor.create_from_latest_messages(messages)
        else:
            updated_cursor = old_cursor.replace_with_latest_messages(messages)
            if updated_cursor.last_scanned_message_id == old_cursor.last_scanned_message_id:
                updated_cursor = None

        if updated_cursor is not None:
            print("Calculated new cursor: " + str(updated_cursor))
            await self._database.upsert_record(updated_cursor)

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
