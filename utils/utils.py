import botocore
import boto3

from config import CONFIG


def get_instance_from_name(ctx, instance_name, ec2=None, table=None):
    if not ec2:
        ec2 = boto3.resource("ec2")
    if not table:
        table = boto3.resource("dynamodb").Table(CONFIG.table)
    item = table.get_item(
        Key={"GuildID": str(ctx.guild.id), "FriendlyName": instance_name}
    )["Item"]
    instance_id = item["InstanceID"]
    try:
        instance = ec2.Instance(instance_id)
        instance.load()
        return instance
    except botocore.exceptions.ClientError as error:
        return None


def user_is_me(ctx):
    return ctx.message.author.id == CONFIG.owner_id
