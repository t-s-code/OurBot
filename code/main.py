# main.py

import argparse, os, sys
from dataclasses import dataclass
from our_bot import OurBot
from models.config import BotConfig, ChannelPruningConfig, ChannelScanningConfig

def main():
    cli_args = read_cli_args()

    config = BotConfig(
        server_id = -1,
        database_channel_id = 1524153385379430601,
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

    bot = OurBot(cli_args.is_dry_run, config)
    bot.run(cli_args.discord_api_token)

@dataclass(frozen=True)
class CliArgs:
    is_dry_run: bool
    discord_api_token: str

def read_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", default="true")
    args = parser.parse_args()

    # dry run
    dry_run_val = args.dry_run.lower()
    if dry_run_val == "true":
        is_dry_run = True
    elif dry_run_val == "false":
        is_dry_run = False
    else:
        raise ValueError("--dry-run must be 'true' or 'false'")

    # discord api token
    discord_api_token = os.environ.get("DISCORD_API_TOKEN", None)
    if discord_api_token is None:
        raise ValueError("DISCORD_API_TOKEN environment variable must be set.")

    return CliArgs(
        is_dry_run=is_dry_run,
        discord_api_token=discord_api_token,
    )


if __name__ == "__main__":
    main()
