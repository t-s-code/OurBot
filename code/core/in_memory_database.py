# core/in_memory_database.py

from models.database.member_activity import MemberActivityRecord
from models.database.channel_scanning_cursor import ChannelScanningCursor

class InMemoryDatabase:
    def __init__(self):
        self._member_activity_record_by_member_id = {}
        self._channel_scanning_cursor_by_channel_id = {}
        self._updated_ids = set()

    def load(self, records):
        for record in records:
            if isinstance(record, MemberActivityRecord):
                self._member_activity_record_by_member_id[record.member_id] = record
            elif isinstance(record, ChannelScanningCursor):
                self._channel_scanning_cursor_by_channel_id[record.channel_id] = record
            else:
                raise ValueError(f"Could not load record of type {record.__class__.__name__}: {record}")

    def get_channel_scanning_cursor(self, channel_id):
        return self._channel_scanning_cursor_by_channel_id.get(channel_id, None)

    def get_member_activity(self, member_id):
        return self._member_activity_record_by_member_id.get(member_id, None)

    def upsert_record(self, record):
        if isinstance(record, MemberActivityRecord):
            existing = self._member_activity_record_by_member_id.get(record.member_id)
            if existing is not None and record.last_seen_message_id <= existing.last_seen_message_id:
                raise ValueError("Expected message id to always increase on updates")
            self. _member_activity_record_by_member_id[record.member_id] = record
            self._updated_ids.add(record.member_id)
        elif isinstance(record, ChannelScanningCursor):
            existing = self._channel_scanning_cursor_by_channel_id.get(record.channel_id)
            if existing is not None and record.last_scanned_message_id <= existing.last_scanned_message_id:
                raise ValueError("Expected message id to always increase on updates")
            self._channel_scanning_cursor_by_channel_id[record.channel_id] = record
            self._updated_ids.add(record.channel_id)
        else:
            raise ValueError(f"Could not upsert record of type {record.__class__.__name__}: {record}")

    def flush_updated_records(self):
        updated_records = []
        for updated_id in self._updated_ids:
            if updated_id in self._member_activity_record_by_member_id:
                updated_records.append(self._member_activity_record_by_member_id[updated_id])
            elif updated_id in self._channel_scanning_cursor_by_channel_id:
                updated_records.append(self._channel_scanning_cursor_by_channel_id[updated_id])
        self._updated_ids.clear()
        return updated_records
