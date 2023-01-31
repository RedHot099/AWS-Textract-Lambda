from cli import aws_access_key_id, aws_secret_access_key, aws_session_token, DEFAULT_VPC
import boto3, time


index = '478874'
key_name = index + '_key'
group_name = index + '_group'
target_name = index + '_target'
lb_name = index + '_loadbalancer'


user_data=r'''
#!/bin/bash
sudo yum update -y
sudo yum install git -y
git clone https://git.wmi.amu.edu.pl/bikol/DPZC-2022-23.git
cd 04_Public_cloud/zadania
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
docker build -t webservice .
docker run -d -p 80:8080 -t webservice
'''

if __name__ == '__main__':
    ec2 = boto3.resource(
        'ec2',
        region_name='us-east-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )

    key_pair = ec2.create_key_pair(
        KeyName=key_name,
        KeyType='ed25519',
        KeyFormat='pem',
    )

    security_group = ec2.create_security_group(
        Description=group_name,
        GroupName=group_name,
        VpcId=DEFAULT_VPC,
    )

    inbound_rules = security_group.authorize_ingress(
        GroupId=security_group.group_id,
        CidrIp='0.0.0.0/0',
        IpProtocol='tcp',
        FromPort=80,
        ToPort=80,
    )

    #TODO instancja EC2
    instance1, instance2 = ec2.create_instances(
        ImageId='ami-0b5eea76982371e91',
        MinCount=2,
        MaxCount=2,
        InstanceType='t2.micro',
        KeyName=key_pair.name,
        UserData=user_data,
        SecurityGroups=[security_group.group_name],
    )

    while True:
        time.sleep(1)
        instance1 = ec2.Instance(instance1.id)
        instance2 = ec2.Instance(instance2.id)
        if instance1.state['Code'] == 16 and instance2.state['Code'] == 16:
            break

    #TODO target group
    elbv2 = boto3.client(
        'elbv2',
        region_name='us-east-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )

    target_group = elbv2.create_target_group(
        Name=target_name,
        Protocol='TCP',
        Port=80,
        VpcId=DEFAULT_VPC,
        TargetType='instance',
        IpAddressType='ipv4',
    )

    registered_targets = elbv2.register_targets(
        TargetGroupArn=target_group['TargetGroups'][0]['TargetGroupArn'],
        Targets=[
            {
                'Id': instance1.id,
                'Port': 80,
            },
            {
                'Id': instance2.id,
                'Port': 80,
            },
        ]
    )

    #TODO elastic IP
    ec2_client = boto3.client(
        'ec2',
        region_name='us-east-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )

    allocation = ec2_client.allocate_address(
        Domain='vpc'
    )

    #TODO load balancer
    load_balancer = elbv2.create_load_balancer(
        Name=lb_name,
        SubnetMappings=[
            {
                'SubnetId': instance1.subnet_id,
                'AllocationId': allocation['AllocationId'],
            },
        ],
        Scheme='internet-facing',
        Type='network',
        IpAddressType='ipv4',
    )

    listener = elbv2.create_listener(
        LoadBalancerArn=load_balancer['LoadBalancers'][0]['LoadBalancerArn'],
        Protocol='TCP',
        Port=80,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group['TargetGroups'][0]['TargetGroupArn'],
            },
        ],
    )

    print(f'{allocation["PublicIp"]}:80')