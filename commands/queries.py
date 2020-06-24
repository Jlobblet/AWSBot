import botocore
import boto3
from boto3.dynamodb.conditions import Key
from discord.ext import commands
from discord.ext.commands import Context, Bot

from config import CONFIG


class Queries(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(CONFIG.table)

    @commands.command(name="show")
    async def show(self, ctx: Context):
        response = self.table.query(
            KeyConditionExpression=Key("GuildID").eq(str(ctx.guild.id))
        )
        await ctx.send(response["Items"])

    @commands.has_permissions(manage_guild=True)
    @commands.command(name="add")
    async def add(self, ctx: Context, FriendlyName, InstanceID):
        Item = {
            "GuildID": str(ctx.guild.id),
            "FriendlyName": FriendlyName,
            "InstanceID": InstanceID,
        }
        self.table.put_item(Item=Item)

    @commands.has_permissions(manage_guild=True)
    @commands.command(name="remove")
    async def remove(self, ctx: Context, FriendlyName):
        self.table.delete_item(
            Key={"GuildID": str(ctx.guild.id), "FriendlyName": FriendlyName}
        )


def setup(bot: Bot):
    bot.add_cog(Queries(bot))
