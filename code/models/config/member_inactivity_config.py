# models/config/member_inactivity_config.py

from dataclasses import dataclass

@dataclass(frozen=True)
class MemberInactivityConfig:
    convert_after_days: int

    def validate(self):
        if self.convert_after_days < 1:
            raise ValueError("convert_after_days must be > 0")
