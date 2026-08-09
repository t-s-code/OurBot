# models/config/channel_scanning_config.py

from dataclasses import dataclass

@dataclass(frozen=True)
class ChannelScanningConfig:
    minutes_between_scans: int

    def validate(self):
        if self.minutes_between_scans < 1:
            raise ValueError("minutes_between_scans must be > 0")
