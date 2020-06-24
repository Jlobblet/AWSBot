#!/usr/bin/env python3
from discord import Message
from discord.ext.commands import Bot, when_mentioned_or

from config import CONFIG

EXTENSIONS = ["commands.instances"]

bot = Bot(command_prefix=when_mentioned_or("%"))


@bot.event
async def on_ready():
    print("Logged in as", str(bot.user), "==========", sep="\n")


@bot.event
async def on_message(message: Message):
    if not message.author.bot:
        await bot.process_commands(message)


if __name__ == "__main__":
    for extension in EXTENSIONS:
        try:
            print(f"Attempting to load {extension}", end="")
            bot.load_extension(extension)
            print("...done")
        except Exception as e:
            exc = f"{type(e).__name__}: {e}"
            print(f"\nFailed to load extension {extension}: {exc}")

    bot.run(CONFIG.token)
