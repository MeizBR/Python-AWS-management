import boto3

ec2_client = boto3.client('ec2', region_name="eu-west-3")
ec2_resource = boto3.resource('ec2')

instances_ids = []

reservations = ec2_client.describe_instances()['Reservations']
for res in reservations:
    instances = res['Instances']
    for ins in instances:
        instances_ids.append(ins['InstanceId'])

response = ec2_resource.create_tags(
    Resources = instances_ids,
    Tags=[
        {
            'Key': 'environment',
            'Value': 'prod'
        }
    ]
)
