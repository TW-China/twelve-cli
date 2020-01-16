import boto3
from terminaltables import SingleTable

from cli.aws_client import Instance, AWSClient


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
