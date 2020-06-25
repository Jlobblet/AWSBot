import datetime
import logging
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
        logging.debug(f"Cooldown information for {instance.instance_id}:")
        logging.debug(f"now        : {now}")
        logging.debug(f"launch_time: {launch_time}")
        logging.debug(f"delta      : {delta}")
        logging.debug(f"os         : {os}")
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
        logging.info(f"Start called on {instance_name}")
        instance = get_instance_from_name(ctx, instance_name, self.ec2, self.table)
        if instance:
            logging.info(f"{instance.instance_id}")
            logging.debug(instance.state["Name"])
            if instance.state["Name"] == "stopped" and self.check_cooldown(instance):
                logging.info("Starting instance...")
                await ctx.send(f"Starting {instance_name}...")
                instance.start()
                self.wait_for_state(instance)
                logging.info("Started")
                await ctx.send("...started")
            else:
                logging.info("Start checks failed, not starting")
                await ctx.send(
                    "The instance is either already running, or on cooldown."
                )
        else:
            logging.info("Instance not found.")
            await ctx.send(f"Instance {instance_name} could not be found.")

    @commands.command(name="stop", help=HELPTEXTS.STOP.full, brief=HELPTEXTS.STOP.brief)
    async def stop_instance(self, ctx: Context, instance_name):
        logging.info(f"Stop called on {instance_name}")
        instance = get_instance_from_name(ctx, instance_name, self.ec2, self.table)
        if instance:
            logging.info(f"{instance.instance_id}")
            logging.debug(instance.state["Name"])
            if instance.state["Name"] == "running":
                logging.info("Stopping instance...")
                await ctx.send(f"Stopping {instance_name}...")
                instance.stop()
                self.wait_for_state(instance)
                logging.info("...stopped")
                await ctx.send("...stopped")
            else:
                logging.info("Already stopped")
                await ctx.send("It's already stopped, silly!")
        else:
            logging.info("Instance not found")
            await ctx.send(f"Instance {instance_name} could not be found.")


def setup(bot: Bot):
    bot.add_cog(InstanceControl(bot))
