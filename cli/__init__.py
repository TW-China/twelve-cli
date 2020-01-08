__version__ = "0.1.0"
import fire
import boto3
from pprint import pprint
from dotenv import load_dotenv
import os

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
        pprint(ret)


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
