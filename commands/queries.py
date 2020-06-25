import botocore
import boto3
from boto3.dynamodb.conditions import Key
from discord.ext import commands
from discord.ext.commands import Context, Bot

from config import CONFIG
from helptexts import HELPTEXTS
from utils.utils import user_is_me


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
        await ctx.send(response["Items"])

    @commands.command(
        name="describe", help=HELPTEXTS.DESCRIBE.full, brief=HELPTEXTS.DESCRIBE.brief
    )
    async def describe(self, ctx: Context, FriendlyName):
        pass

    @commands.check(user_is_me)
    @commands.command(name="add", help=HELPTEXTS.ADD.full, brief=HELPTEXTS.ADD.brief)
    async def add(self, ctx: Context, FriendlyName, InstanceID):
        Item = {
            "GuildID": str(ctx.guild.id),
            "FriendlyName": FriendlyName,
            "InstanceID": InstanceID,
        }
        self.table.put_item(Item=Item)

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
