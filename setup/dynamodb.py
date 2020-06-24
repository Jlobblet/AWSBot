#!/usr/bin/env python3
import json

import botocore
import boto3

param_loc = "friendly_name_table.json"

if __name__ == "__main__":
    dynamodb = boto3.resource("dynamodb")

    print(f"Loading table parameters from {param_loc}...")
    with open(param_loc, "r") as json_file:
        table_params = json.loads(json_file.read())
    print("...loaded")

    print("Creating new table...")
    table = dynamodb.create_table(**table_params)
    table.meta.client.get_waiter("table_exists").wait(
        TableName=table_params["TableName"]
    )
    print("...done")
else:
    print("Trying to run dynamodb setup not as __main__, exiting.")
