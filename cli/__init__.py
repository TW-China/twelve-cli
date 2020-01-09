__version__ = "0.1.0"

from dataclasses import dataclass

import fire
import boto3
from pprint import pprint
from dotenv import load_dotenv
import os
from terminaltables import SingleTable
from collections import namedtuple
from typing import List

NEEDED_ENVIRONMENT_VARIABLES = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
]

Instance = namedtuple("Instance", "id name type public_ip pricate_ip status")


class AWSClient:
    @staticmethod
    def get_all_ec2_instance() -> List[Instance]:
        ec2 = boto3.client("ec2")
        ret = ec2.describe_instances()
        data = []
        for reservation in ret.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                named_tag = list(
                    map(
                        lambda i: i["Value"],
                        filter(lambda i: i["Key"] == "Name", instance.get("Tags", {})),
                    )
                )
                name = named_tag[0] if len(named_tag) > 0 else ""
                i = Instance(
                    instance.get("InstanceId"),
                    name,
                    instance.get("InstanceType"),
                    instance.get("PublicIpAddress"),
                    instance.get("PrivateIpAddress"),
                    instance.get("State", {}).get("Name"),
                )
                data.append(i)
        return data


class EC2:
    @staticmethod
    def list():
        """get all ecs instances"""
        data = AWSClient.get_all_ec2_instance()

        data.insert(
            0, Instance("ID", "Name", "Type", "Public IP", "Private IP", "Status")
        )
        table = SingleTable(data)
        print(table.table)

    @staticmethod
    def stop(id=None, wait=False):
        """stop all instance or specific id for only one instance"""

        if id is not None:
            ids = [id]
        else:
            instances = AWSClient.get_all_ec2_instance()
            ids = map(
                lambda i: i.id, filter(lambda i: i.status == "running", instances)
            )

        for current_instance_id in ids:

            ec2 = boto3.resource("ec2")
            instance = ec2.Instance(current_instance_id)
            instance.stop()
            print(f"[ID: {current_instance_id}] stop command is sent")
            if wait:
                print(f"waiting instance {current_instance_id} stop...")
                instance.wait_until_stopped()
                print(f"instance {current_instance_id} stopped")

    def resume(self, id=None, wait=False):
        """resume all instance or specific id for only one instance"""

        if id is not None:
            ids = [id]
        else:
            instances = AWSClient.get_all_ec2_instance()
            ids = map(
                lambda i: i.id, filter(lambda i: i.status == "stopped", instances)
            )

        for current_instance_id in ids:

            ec2 = boto3.resource("ec2")
            instance = ec2.Instance(current_instance_id)
            instance.start()
            print(f"[ID: {current_instance_id}] resume command is sent")
            if wait:
                print(f"waiting instance {current_instance_id} start...")
                instance.wait_until_running()
                print(f"instance {current_instance_id} started")


class Commands:
    def __init__(self):
        self.ec2 = EC2()

    @staticmethod
    def doctor():
        for variable in NEEDED_ENVIRONMENT_VARIABLES:
            if os.getenv(variable, None) is None:
                print(f"Environment variable '{variable}' must be set")
        else:
            print("all seems good")


if __name__ == "__main__":
    load_dotenv()
    fire.Fire(Commands)
