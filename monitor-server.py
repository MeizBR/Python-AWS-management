import requests
import smtplib
import os
import paramiko
import boto3
import time

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

ec2_client = boto3.client('ec2', region_name="eu-west-3")

instance_id = ""
instance_status = ""

reservations = ec2_client.describe_instances()
for reservation in reservations["Reservations"]:
    instances = reservation["Instances"]
    for instance in instances:
        instance_id = instance['InstanceId']
        instance_status = instance['State']['Name']

def send_notification(email_msg):
    print("Sending email ...")
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: SITE DOWN\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

def restart_container():
    print("Restarting the container ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("15.236.206.35", username="ubuntu", key_filename="/home/meiezbr/.ssh/ec2-instance-terraform.pem")
    stdin,stdout, stderr = ssh.exec_command("docker start f94ab1b5bab6")
    print(stdout.readlines())
    ssh.close()
    print("Application is restarted !")

try:
    response = requests.get("http://ec2-15-236-206-35.eu-west-3.compute.amazonaws.com/")
    if response.status_code == 200:
        print("application is running successfully !")
    else:
        print("application is down, fix it !")
        msg = "Application status code is {response.status_code} !"
        send_notification(msg)

        # restart the application
        restart_container()

except Exception as ex:
    print(f"connection error happened : {ex}")
    msg = "Application is not accessible at all !"
    send_notification(msg)

    # restart the server
    ec2_client.reboot_instances(
        InstanceIds=[
            instance_id
        ]
    )
    print("Server is restarted !")

    # restart the application
    while True:
        if instance_status == "running":
            time.sleep(5)
            restart_container()
            break
        else:
            print("Server hasn't been ready yet !")