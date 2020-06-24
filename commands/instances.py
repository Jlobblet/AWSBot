import botocore
import boto3
from discord.ext import commands
from discord.ext.commands import Context, Bot

from utils.utils import get_instance


def start_instance(instance_id, ec2=None):
    instance = get_instance(instance_id, ec2)
    state = instance.state & int("11111111", 2)
    if state == 80:
        try:
            response = instance.start()
            return response
        except botocore.exceptions.ClientError as error:
            print(error)
            return error
    else:
        return None


def stop_instance(instance_id, ec2=None):
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

    @commands.command(name="start")
    async def start_instance(self, ctx: Context, instance_name):
        raise NotImplementedError

    @commands.command(name="stop")
    async def stop_instance(self, ctx: Context, instance_name):
        raise NotImplementedError


def setup(bot: Bot):
    bot.add_cog(InstanceControl(bot))
