# models/config/channel_pruning_config.py

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class ChannelPruningConfig:
    channel_name: str
    channel_id: int
    days_until_delete_messages_from_channel: Optional[int] = None
    days_until_delete_messages_from_threads: Optional[int] = None
    message_ids_to_keep: List[int] = field(default_factory=list)
    thread_ids_to_keep: List[int] = field(default_factory=list)
    delete_threads_when_last_message_deleted: bool = False

    def validate(self):
        if self.days_until_delete_messages_from_channel is None and self.days_until_delete_messages_from_threads is None:
            raise ValueError("days_until_delete_messages_from_channel or days_until_delete_messages_from_threads must be defined")

        if self.days_until_delete_messages_from_channel is not None and self.days_until_delete_messages_from_channel < 1:
            raise ValueError("days_until_delete_messages_from_channel must be > 0")

        if self.days_until_delete_messages_from_threads is not None and self.days_until_delete_messages_from_threads < 1:
            raise ValueError("days_until_delete_messages_from_threads must be > 0")
