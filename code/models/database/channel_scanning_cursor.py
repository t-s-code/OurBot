# models/database/channel_scanning_cursor.py

from dataclasses import dataclass
from datetime import datetime
from typing import List

from .thread_scanning_cursor import ThreadScanningCursor

@dataclass(frozen=True)
class ChannelScanningCursor:
    channel_name: str
    channel_id: int
    last_scanned_message_id: int
    last_scanned_message_timestamp: datetime
    thread_scanning_cursors: List[ThreadScanningCursor]

    @staticmethod
    def create_from_latest_messages(messages):
        if len(messages) == 0:
            return None
        else:
            last_message = messages[-1]
            return ChannelScanningCursor(
                    channel_name=last_message.channel.name,
                    channel_id=last_message.channel.id,
                    last_scanned_message_id=last_message.id,
                    last_scanned_message_timestamp=last_message.created_at,
                    thread_scanning_cursors = []
            )

    def replace_with_latest_messages(self, messages):
        if len(messages) == 0:
            return self
        else:
            last_message = messages[-1]
            return self.replace(
                    last_scanned_message_id=last_message.id,
                    last_scanned_message_timestamp=last_message.created_at
            )
