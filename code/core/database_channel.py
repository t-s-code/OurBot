# core/database_channel.py

import re
from datetime import datetime, timezone
from models.database.member_activity import MemberActivityRecord, MemberActivityStatus
from models.database.channel_scanning_cursor import ChannelScanningCursor

class DatabaseChannel:
    _TIMESTAMP_FORMAT = "%Y-%m-%d - %H:%M:%S UTC"

    def __init__(self, discord_client, config):
        self._discord_client = discord_client
        self._config = config
        self._message_id_by_key = {}
        self._activity_db_channel = None
        self._scanning_db_channel = None

    async def load(self):
        records = []

        self._activity_db_channel = self._discord_client.get_channel(self._config.activity_db_channel_id)
        async for message in self._activity_db_channel.history(limit=None, oldest_first=True):
            record = self.deserialize_member_activity_record(message)
            self._message_id_by_key[record.member_id] = message.id
            records.append(record)

        self._scanning_db_channel = self._discord_client.get_channel(self._config.scanning_db_channel_id)
        async for message in self._scanning_db_channel.history(limit=None, oldest_first=True):
            record = self.deserialize_channel_scanning_cursor(message)
            self._message_id_by_key[record.channel_id] = message.id
            records.append(record)

        return records

    async def upsert_record(self, record):
        text = None
        key = None

        if isinstance(record, MemberActivityRecord):
            key = record.member_id
            text = self.serialize_member_activity_record(record)
            channel = self._activity_db_channel
        elif isinstance(record, ChannelScanningCursor):
            key = record.channel_id
            text = self.serialize_channel_scanning_cursor(record)
            channel = self._scanning_db_channel
        else:
            raise ValueError(f"Unexpected record type: {record.__class__.__name__}: {record}")

        message_id = self._message_id_by_key.get(key, None)
        created_message_id = await self._upsert_record(channel, text, message_id)
        if created_message_id is not None:
            self._message_id_by_key[key] = created_message_id

    async def _upsert_record(self, channel, text, message_id):
        if message_id is None:
            if self._config.dry_run:
                print(f"Would have created new message in {channel.name}: {text}")
                return None
            else:
                sent_message = await channel.send(text)
                return sent_message.id
        else:
            if self._config.dry_run:
                print(f"Would have edited message={message_id} in {channel.name}: {text}")
            else:
                message = channel.get_partial_message(message_id)
                await message.edit(content=text)
            return None

    # SERIALIZERS AND DESERIALIZERS
    #
    # TODO: Move to own file

    def serialize_member_activity_record(self, record):
        timestamp_str = record.last_seen_message_timestamp.strftime(self._TIMESTAMP_FORMAT)
        return (
            "MemberActivityRecord\n"
            f"- Name: {record.member_name}\n"
            f"- Id: {record.member_id}\n"
            f"- Status: {record.status.value}\n"
            f"- Last seen message id: {record.last_seen_message_id}\n"
            f"- Last seen message timestamp: {timestamp_str}"
        )

    def deserialize_member_activity_record(self, message):
        pattern = (
            r"^MemberActivityRecord\n"
            r"- Name: (?P<name>.+)\n"
            r"- Id: (?P<id>\d+)\n"
            r"- Status: (?P<status>.+)\n"
            r"- Last seen message id: (?P<last_seen_message_id>\d+)\n"
            r"- Last seen message timestamp: (?P<timestamp>.+)$"
        )
        match = re.match(pattern, message.content.strip())
        if not match:
            raise ValueError(f"Could not deserialize message due to unexpected format:\n{message.content}")

        try:
            gd = match.groupdict()
            timestamp = datetime.strptime(gd["timestamp"], self._TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc)
            return MemberActivityRecord(
                member_name=gd["name"],
                member_id=int(gd["id"]),
                status=MemberActivityStatus(gd["status"]),
                last_seen_message_id=int(gd["last_seen_message_id"]),
                last_seen_message_timestamp=timestamp
            )
        except Exception:
            raise ValueError(f"Could not deserialize message due to unexpected format:\n{message.content}")

    def serialize_channel_scanning_cursor(self, cursor):
        timestamp_str = cursor.last_scanned_message_timestamp.strftime(self._TIMESTAMP_FORMAT)
        return (
            "ChannelScanningCursor\n"
            f"- Channel: {cursor.channel_name}\n"
            f"- Id: {cursor.channel_id}\n"
            f"- Last scanned message id: {cursor.last_scanned_message_id}\n"
            f"- Last scanned message timestamp: {timestamp_str}"
        )

    def deserialize_channel_scanning_cursor(self, message):
        pattern = (
            r"^ChannelScanningCursor\n"
            r"- Channel: (?P<name>.+)\n"
            r"- Id: (?P<id>\d+)\n"
            r"- Last scanned message id: (?P<last_scanned_message_id>\d+)\n"
            r"- Last scanned message timestamp: (?P<timestamp>.+)$"
        )
        match = re.match(pattern, message.content.strip())
        if not match:
            raise ValueError(f"Could not deserialize message due to unexpected format:\n{message.content}")

        try:
            gd = match.groupdict()
            timestamp = datetime.strptime(gd["timestamp"], self._TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc)
            return ChannelScanningCursor(
                channel_name=gd["name"],
                channel_id=int(gd["id"]),
                last_scanned_message_id=int(gd["last_scanned_message_id"]),
                last_scanned_message_timestamp=timestamp,
                thread_scanning_cursors=[]
            )
        except Exception:
            raise ValueError(f"Could not deserialize message due to unexpected format:\n{message.content}")
