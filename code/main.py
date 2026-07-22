# main.py

import argparse, os, sys
from dataclasses import dataclass
from our_bot import OurBot
from models.config import BotConfig, ChannelPruningConfig, ChannelScanningConfig

def main():
    cli_args = _read_cli_args()
    discord_api_token = _read_discord_api_token()

    config = BotConfig(
        dry_run = cli_args.dry_run,
        server_id = 1356994559485153442,
        activity_db_channel_id = 1524153385379430601,
        scanning_db_channel_id = 1529551272372469861,
        channel_scanning_config = ChannelScanningConfig(
            minutes_between_scans = 5
        ),
        channel_pruning_configs = [
            ChannelPruningConfig(
                channel_name="Rules",
                channel_id=1356995099598389338,
                days_until_delete_messages_from_channel=3,
            )
        ]
    )

    bot = OurBot(config)
    bot.run(discord_api_token)

@dataclass(frozen=True)
class CliArgs:
    dry_run: bool

def _read_discord_api_token():
    discord_api_token = os.environ.get("DISCORD_API_TOKEN", None)
    if discord_api_token is None:
        raise ValueError("DISCORD_API_TOKEN environment variable must be set.")
    return discord_api_token

def _read_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", default="true")
    args = parser.parse_args()

    dry_run_val = args.dry_run.lower()
    if dry_run_val == "true":
        dry_run = True
    elif dry_run_val == "false":
        dry_run = False
    else:
        raise ValueError("--dry-run must be 'true' or 'false'")

    return CliArgs(
        dry_run=dry_run,
    )


if __name__ == "__main__":
    main()
