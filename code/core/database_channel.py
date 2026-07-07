# core/database_channel.py

import re
from datetime import datetime
from models.database.member_activity import MemberActivityRecord, MemberActivityStatus
from models.database.channel_scanning_cursor import ChannelScanningCursor

class DatabaseChannel:
    def __init__(self, discord_client, config):
        self._discord_client = discord_client
        self._config = config
        self._member_id_to_message_id = {}
        self._discord_channel = None

    async def load(self):
        self._discord_channel = self._discord_client.get_channel(self._config.database_channel_id)
        # TODO
        return []

    async def upsert_record(self, record):
        text = None
        message_id = None

        if isinstance(record, MemberActivityRecord):
            message_id = self._member_id_to_message_id.get(record.member_id, None)
            text = self.serialize_member_activity_record(record)
        elif isinstance(record, ChannelScanningCursor):
            pass
        else:
            raise ValueError(f"Unexpected record type: {record.__class__.__name__}: {record}")

        await self._write_record(text, message_id)

    async def _write_record(self, text, message_id):
        if message_id is None:
            if self._config.dry_run:
                print(f"Would have created new message in #bot-database: {text}")
            else:
                await self._discord_channel.send(text)
        else:
            if self._config.dry_run:
                print(f"Would have edited message={message_id} in #bot-database: {text}")
            else:
                message = self._discord_channel.get_partial_message(message_id)
                await message.edit(content=text)

    def serialize_member_activity_record(self, record):
        timestamp_str = record.last_seen_message_timestamp.strftime("%Y-%m-%d - %H:%M:%S UTC")
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
            raise ValueError(f"Could not deserialize message due to unexpected format: {message.jump_url}")

        try:
            gd = match.groupdict()
            timestamp = datetime.strptime(gd["timestamp"], "%Y-%m-%d - %H:%M:%S UTC")
            return MemberActivityRecord(
                member_name=gd["name"],
                member_id=int(gd["id"]),
                status=MemberActivityStatus(gd["status"]),
                last_seen_message_id=int(gd["last_seen_message_id"]),
                last_seen_message_timestamp=timestamp
            )
        except Exception:
            raise ValueError(f"Could not deserialize message due to unexpected format: {message.jump_url}")

    def serialize_channel_scanning_cursor(self, cursor):
        pass

    def deserialize_channel_scanning_cursor(self, message):
        pass
