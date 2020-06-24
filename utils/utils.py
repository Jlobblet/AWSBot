import botocore
import boto3


def get_instance(instance_id, ec2=None):
    if not ec2:
        ec2 = boto3.resource("ec2")
    return ec2.Instance(instance_id)
