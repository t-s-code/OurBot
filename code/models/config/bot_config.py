# models/config/bot_config.py

from dataclasses import dataclass
from typing import List

from .channel_scanning_config import ChannelScanningConfig 
from .channel_pruning_config import ChannelPruningConfig

@dataclass(frozen=True)
class BotConfig:
    dry_run: bool
    server_id: int
    database_channel_id: int
    channel_scanning_config: ChannelScanningConfig
    channel_pruning_configs: List[ChannelPruningConfig]
    
    def validate(self):
        self.channel_scanning_config.validate()

        seen_ids = set()
        
        for c in self.channel_pruning_configs:
            seen_ids.add(c.channel_id)
            c.validate()

        if len(seen_ids) != len(self.channel_pruning_configs):
            raise ValueError("Every channel_id in channel_pruning_configs must be unique")
