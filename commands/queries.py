import datetime
import logging

import botocore
import boto3
from boto3.dynamodb.conditions import Key
from discord.ext import commands
from discord.ext.commands import Context, Bot

from config import CONFIG
from helptexts import HELPTEXTS
from utils.utils import get_instance_from_name, user_is_me


class Queries(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.ec2 = boto3.resource("ec2")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(CONFIG.table)

    @commands.command(name="show", help=HELPTEXTS.SHOW.full, brief=HELPTEXTS.SHOW.brief)
    async def show(self, ctx: Context):
        response = self.table.query(
            KeyConditionExpression=Key("GuildID").eq(str(ctx.guild.id))
        )
        msg = "\n".join(
            (
                "{}: {}".format(x["FriendlyName"], x["InstanceID"])
                for x in response["Items"]
            )
        )
        await ctx.send(msg)

    @commands.command(
        name="describe", help=HELPTEXTS.DESCRIBE.full, brief=HELPTEXTS.DESCRIBE.brief
    )
    async def describe(self, ctx: Context, FriendlyName):
        instance = get_instance_from_name(ctx, FriendlyName, self.ec2, self.table)
        instance.load()
        state = instance.state["Name"]
        time = datetime.datetime.now().replace(second=0) - instance.launch_time.replace(
            tzinfo=None, second=0
        )

        await ctx.send(f"{FriendlyName} is currently {state}.")
        if state == "running":
            await ctx.send(
                f"It has been running since {instance.launch_time}, for a duration of {time}."
            )
        elif state == "stopped":
            await ctx.send(f"It was last started {time} ago.")

    @commands.check(user_is_me)
    @commands.command(name="add", help=HELPTEXTS.ADD.full, brief=HELPTEXTS.ADD.brief)
    async def add(self, ctx: Context, FriendlyName, InstanceID):
        try:
            instance = self.ec2.Instance(InstanceID)
            instance.load()
            Item = {
                "GuildID": str(ctx.guild.id),
                "FriendlyName": FriendlyName,
                "InstanceID": InstanceID,
            }
            self.table.put_item(Item=Item)
        except botocore.exceptions.ClientError as error:
            await ctx.send(f"ClientError:\n{error}")

    @commands.check(user_is_me)
    @commands.command(
        name="remove", help=HELPTEXTS.REMOVE.full, brief=HELPTEXTS.REMOVE.brief
    )
    async def remove(self, ctx: Context, FriendlyName):
        self.table.delete_item(
            Key={"GuildID": str(ctx.guild.id), "FriendlyName": FriendlyName}
        )


def setup(bot: Bot):
    bot.add_cog(Queries(bot))
