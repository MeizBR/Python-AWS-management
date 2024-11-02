import boto3
import schedule
import time

ec2_client = boto3.client('ec2', region_name="eu-west-3")
ec2_resource = boto3.resource('ec2')

f = open("instance_status_output.txt", "a")

def check_instance_status():
    reservations = ec2_client.describe_instances()
    for reservation in reservations["Reservations"]:
        instances = reservation["Instances"]
        for instance in instances:
            print(f"instance {instance['InstanceId']} is {instance['State']['Name']}")
            f.write(f"instance {instance['InstanceId']} is {instance['State']['Name']}\n")
    print("####################")
    f.write("####################\n")

schedule.every(5).seconds.do(check_instance_status)

while True:
    schedule.run_pending()

f.close()