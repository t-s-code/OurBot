# models/database/thread_scanning_cursor.py

from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ThreadScanningCursor:
    channel_id: int
    thread_id: int
    last_scanned_message_id: int
    last_scanned_message_timestamp: datetime
