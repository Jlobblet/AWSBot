#!/usr/bin/env python3
import logging

from discord import Message
from discord.ext.commands import Bot, when_mentioned_or

from config import CONFIG

EXTENSIONS = ["commands.instances", "commands.queries"]

bot = Bot(command_prefix=when_mentioned_or("%"))


@bot.event
async def on_ready():
    logging.info(f"Logged in as {str(bot.user)}")


@bot.event
async def on_message(message: Message):
    await bot.process_commands(message)


if __name__ == "__main__":
    for extension in EXTENSIONS:
        try:
            logging.info(f"Attempting to load {extension}", end="")
            bot.load_extension(extension)
            logging.info("...done")
        except Exception as e:
            exc = f"{type(e).__name__}: {e}"
            logging.error(f"\nFailed to load extension {extension}: {exc}")

    bot.run(CONFIG.token)
