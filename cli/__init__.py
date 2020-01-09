__version__ = "0.1.0"

import fire
import boto3
from pprint import pprint
from dotenv import load_dotenv
import os
from terminaltables import SingleTable

NEEDED_ENVIRONMENT_VARIABLES = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
]


class EC2:
    def list(self):
        """get all ecs instances"""
        ec2 = boto3.client("ec2")
        ret = ec2.describe_instances()
        data = [["ID", "Type", "Public IP", "Private IP", "Status"]]
        for reservation in ret.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                data.append(
                    [
                        instance.get("InstanceId"),
                        instance.get("InstanceType"),
                        instance.get("PublicIpAddress"),
                        instance.get("PrivateIpAddress"),
                        instance.get("State", {}).get("Name"),
                    ]
                )
        table = SingleTable(data)
        print(table.table)

    def stop(self, id, wait=False):
        """stop all instance or specific id for only one instance"""
        ec2 = boto3.resource("ec2")
        instance = ec2.Instance(id)
        instance.stop()
        print("stop command is sent")
        if wait:
            print(f"waiting instance {id} stop...")
            instance.wait_until_stopped()
            print(f"instance {id} stopped")

    def resume(self, id, wait=False):
        """resume all instance or specific id for only one instance"""
        ec2 = boto3.resource("ec2")
        instance = ec2.Instance(id)
        instance.start()
        print("resume command is sent")
        if wait:
            print(f"waiting instance {id} start...")
            instance.wait_until_running()
            print(f"instance {id} started")


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
