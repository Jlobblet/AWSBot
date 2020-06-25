import datetime
import time

import botocore
import boto3
from discord.ext import commands
from discord.ext.commands import Context, Bot

from config import CONFIG
from helptexts import HELPTEXTS
from utils.utils import get_instance_from_name


class InstanceControl(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.ec2 = boto3.resource("ec2")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(CONFIG.table)

    def get_os(self, tags):
        for tag in tags:
            if tag["Key"] == "os":
                return tag["Value"]
        return None

    def check_cooldown(self, instance):
        os = self.get_os(instance.tags)
        launch_time = instance.launch_time.replace(tzinfo=None)
        now = datetime.datetime.now().replace(tzinfo=None)
        delta = now - launch_time
        if os == "linux" and delta > datetime.timedelta(minutes=1):
            return True
        elif delta > datetime.timedelta(hours=1):
            return True
        return False

    def wait_for_state(self, instance):
        while instance.state["Name"] not in ("running", "stopping"):
            time.sleep(5)
            instance.load()
        return True

    @commands.command(
        name="start", help=HELPTEXTS.START.full, brief=HELPTEXTS.START.brief
    )
    async def start_instance(self, ctx: Context, instance_name):
        instance = get_instance_from_name(ctx, instance_name, self.ec2, self.table)
        if instance:
            if instance.state["Name"] == "stopped" and self.check_cooldown(instance):
                await ctx.send(f"Starting {instance_name}...")
                instance.start()
                self.wait_for_state(instance)
                await ctx.send("...started")
            else:
                await ctx.send(
                    "The instance is either already running, or on cooldown."
                )
        else:
            await ctx.send(f"Instance {instance_name} could not be found.")

    @commands.command(name="stop", help=HELPTEXTS.STOP.full, brief=HELPTEXTS.STOP.brief)
    async def stop_instance(self, ctx: Context, instance_name):
        instance = get_instance_from_name(ctx, instance_name, self.ec2, self.table)
        if instance:
            if instance.state["Name"] == "running":
                await ctx.send(f"Stopping {instance_name}...")
                instance.stop()
                self.wait_for_state(instance)
                await ctx.send("...stopped")
            else:
                await ctx.send("It's already stopped, silly!")
        else:
            await ctx.send(f"Instance {instance_name} could not be found.")


def setup(bot: Bot):
    bot.add_cog(InstanceControl(bot))
