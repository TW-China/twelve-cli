__version__ = "0.1.0"

import os


from cli.cluster import Cluster
from cli.ec2 import EC2

NEEDED_ENVIRONMENT_VARIABLES = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
]


class Commands:
    def __init__(self):
        self.ec2 = EC2()
        self.cluster = Cluster

    @staticmethod
    def doctor():
        for variable in NEEDED_ENVIRONMENT_VARIABLES:
            if os.getenv(variable, None) is None:
                print(f"Environment variable '{variable}' must be set")
        else:
            print("all seems good")



