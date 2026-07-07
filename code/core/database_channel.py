# core/database_channel.py

import re
from datetime import datetime
from models.database.member_activity import MemberActivityRecord, MemberActivityStatus

class DatabaseChannel:
    def __init__(self, discord_client, is_dry_run):
        self._discord_client = discord_client
        self._is_dry_run = is_dry_run

    async def read_database(self):
        pass

    async def upsert_record(self, record):
        pass

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
