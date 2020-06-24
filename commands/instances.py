import datetime
import time

import botocore
import boto3
from discord.ext import commands
from discord.ext.commands import Context, Bot

from config import CONFIG


def stop_instance(instance_id, ec2):
    instance = get_instance(instance_id, ec2)
    state = instance.state & int("11111111", 2)
    if state == 16:
        try:
            response = instance.stop()
            return response
        except botocore.exceptions.ClientError as error:
            print(error)
            return error
    else:
        return None


def describe_instance(instance_id, ec2=None):
    instance = get_instance(instance_id, ec2)


class InstanceControl(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.ec2 = boto3.resource("ec2")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(CONFIG.table)

    def get_instance_from_name(self, ctx, instance_name):
        item = self.table.get_item(
            Key={"GuildID": str(ctx.guild.id), "FriendlyName": instance_name}
        )["Item"]
        instance_id = item["InstanceID"]
        try:
            instance = self.ec2.Instance(instance_id)
            instance.load()
            return instance
        except botocore.exceptions.ClientError as error:
            return None

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

    @commands.command(name="start")
    async def start_instance(self, ctx: Context, instance_name):
        instance = self.get_instance_from_name(ctx, instance_name)
        if instance:
            if instance.state["Name"] == "stopped" and self.check_cooldown(instance):
                await ctx.send(f"Starting {instance_name}...")
                instance.start()
                self.wait_for_state(instance)
                await ctx.send("...started")
            else:
                await ctx.send(
                    "The instance is either already stopped, or on cooldown."
                )
        else:
            await ctx.send(f"Instance {instance_name} could not be found.")

    @commands.command(name="stop")
    async def stop_instance(self, ctx: Context, instance_name):
        instance = self.get_instance_from_name(ctx, instance_name)
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
