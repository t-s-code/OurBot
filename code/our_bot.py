# our_bot.py

import asyncio
import discord
from discord import app_commands

from core.database import Database
from jobs import ChannelScanningJob

class OurBot:
    def __init__(self, config):
        self._config = config

        self._config.validate()

        self._discord_client = discord.Client(
            intents=self._build_intents()
        )
        self._command_tree = app_commands.CommandTree(self._discord_client)

        self._database = Database(
            discord_client=self._discord_client,
            config=self._config
        )

        self._channel_scanning_job = ChannelScanningJob(
            discord_client=self._discord_client,
            database=self._database,
            config=self._config
        )

        self._register_events()
        self._register_commands()

    # -------------------------
    # Discord Setup
    # -------------------------

    def _build_intents(self):
        intents = discord.Intents.default()
        intents.message_content = False
        intents.members = True
        return intents

    def _register_events(self):
        @self._discord_client.event
        async def on_ready():
            await self._on_ready()

        @self._discord_client.event
        async def on_message(message):
            await self._on_message(message)

        @self._discord_client.event
        async def on_error(event, *args, **kwargs):
            import sys, traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"\nUnhandled error! Exiting...\n{exc_type.__name__}: {exc_value}", file=sys.stderr)
            traceback.print_tb(exc_traceback, file=sys.stderr)
            print("", file=sys.stderr)
            await self._discord_client.close()

    def _register_commands(self):
        hf_group = app_commands.Group(name="hf", description="Housekeeping bot commands")

        @hf_group.command(name="off", description="Shuts down the bot")
        async def off(interaction: discord.Interaction):
            await interaction.response.send_message("Shutting down...")
            await self._discord_client.close()

        self._command_tree.add_command(hf_group)

    # -------------------------
    # Event Handlers
    # -------------------------
  
    async def _on_ready(self):
        bot_user = self._discord_client.user
        print(f"Logged in as {bot_user.display_name} ({bot_user.id})")

        await self._command_tree.sync()

        await self._database.load()
        channel_scanning_task = asyncio.create_task(self._channel_scanning_job.run())

        await channel_scanning_task

    async def _on_message(self, message):
        await self._channel_scanning_job.on_message(message)

    # -------------------------
    # Run
    # -------------------------

    def run(self, token):
        self._discord_client.run(token)
