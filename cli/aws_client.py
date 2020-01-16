from collections import namedtuple
from typing import List

import boto3

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
