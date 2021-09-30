import logging
import typing as t
from pathlib import Path

import hikari
import sake
import tanjun

from hikari_testing import STDOUT_CHANNEL_ID, TEST_GUILD_ID, __version__

_BotT = t.TypeVar("_BotT", bound="Bot")


class Bot(hikari.GatewayBot):
    __slots__ = ("client", "stdout_channel")

    def __init__(self: _BotT) -> None:
        with open("./secrets/token") as f:
            token = f.read().strip("\n")

        super().__init__(
            token=token,
            intents=hikari.Intents.ALL,
        )

    def create_client(self: _BotT) -> None:
        client = tanjun.Client.from_gateway_bot(self, set_global_commands=TEST_GUILD_ID)
        client.load_modules(*Path("./modules").glob("*.py"))

    def run(self: _BotT) -> None:
        self.create_client()

        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)

        super().run(
            activity=hikari.Activity(
                name=f"to some absolute bangers | Version {__version__}",
                type=hikari.ActivityType.LISTENING,
            )
        )

    async def on_starting(self: _BotT, event: hikari.StartingEvent) -> None:
        cache = sake.redis.RedisCache(self, self, address="redis://127.0.0.1")
        await cache.open()
        logging.info("Connected to Redis server")

    async def on_started(self: _BotT, event: hikari.StartedEvent) -> None:
        self.stdout_channel = await self.rest.fetch_channel(STDOUT_CHANNEL_ID)
        await self.stdout_channel.send(f"Testing v{__version__} now online!")

        logging.info("Bot ready")

    async def on_stopping(self: _BotT, event: hikari.StoppingEvent) -> None:
        # This is gonna be fixed.
        # await self.stdout_channel.send(f"Testing v{__version__} is shutting down.")
        ...
