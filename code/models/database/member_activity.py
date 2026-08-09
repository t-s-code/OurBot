# models/database/member_activity.py

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum

class MemberActivityStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

    @staticmethod
    def from_discord_member(member):
        for role in member.roles:
            if role.name == "Member" \
                    or role.name == "Established Member":
                return MemberActivityStatus.ACTIVE
        return MemberActivityStatus.INACTIVE

@dataclass(frozen=True)
class MemberActivityRecord:
    member_name: str
    member_id: int
    status: MemberActivityStatus
    last_seen_message_id: int
    last_seen_message_timestamp: datetime

    @staticmethod
    def create_from_message(message):
        return MemberActivityRecord(
                member_name=message.author.display_name,
                member_id=message.author.id,
                status=MemberActivityStatus.from_discord_member(message.author),
                last_seen_message_id=message.id,
                last_seen_message_timestamp=message.created_at
        )

    def replace_with_latest_message(self, message):
        if self.last_seen_message_id < message.id:
            return replace(
                    self,
                    member_name=message.author.display_name,
                    last_seen_message_id=message.id,
                    last_seen_message_timestamp=message.created_at
            )
        else:
            return self
