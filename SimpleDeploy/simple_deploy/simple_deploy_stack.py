from unicodedata import name
import aws_cdk as cdk
import aws_cdk as core
from aws_cdk.aws_ec2 import SubnetSelection

from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment ,
    aws_ec2 as ec2,
    aws_iam as iam
)
import os
from constructs import Construct

class SimpleDeployStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Override the logical ID of the bucket construct
        bucket_logical_id = "my-unique-artifactory"

        #creating S3 bucket 
        bucket = s3.Bucket(self, bucket_logical_id,
            bucket_name="my-unique-artifactory",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)

        # Upload a local file to the bucket
        deployment = s3_deployment.BucketDeployment(self, "DeployStaticWebsite",
            sources=[s3_deployment.Source.asset("D:\projects\SimpleDeploy\/app\/bloodbank.zip")],
            destination_bucket=bucket,
        )
        # Grant public read access to the bucket
        # bucket.grant_public_access()

        # core.CfnOutput(self, "BucketNameOutput",
        #     value=bucket.bucket_name,
        #     description="The name of the deployed S3 bucket"
        # )

        # bucket_name = core.Fn.import_value("")

        # Creates a VPC for the EC2 instance
        vpc = ec2.Vpc(
            self, "InstanceVpc",
            cidr="10.0.0.0/16"
        )

        # Creates a security group for the EC2 instance
        instance_sg = ec2.SecurityGroup(
            self, "InstanceSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )
        # Allows inbound SSH access to the EC2 instance
        instance_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="Allow SSH access and http access",
            remote_rule=False
        )
        instance_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(8000),
            description="Allow access on port 8000",
            remote_rule=False
        )
        instance_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow access on port 80 http traffic",
            remote_rule=False
        )

        instance_role = iam.Role(
            self, "InstanceRole",
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com')
        )
        # # Create an IAM policy for PutBucketPolicy
        # bucket_policy = iam.PolicyStatement(
        #     effect=iam.Effect.ALLOW,
        #     actions=["s3:PutBucketPolicy"],
        #     resources=[bucket.bucket_arn]
        # )

        # # Attach the IAM policy to the instance role
        # instance_role.add_to_policy(bucket_policy)

        # Attach AmazonS3FullAccess policy to the IAM role
        instance_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess')
        )

        # Create user data
        user_data = ec2.UserData.for_linux()
        user_data.add_commands("""
                #!/bin/bash
                sudo apt update -y
                sudo apt install python3 -y
                sudo apt install python3-pip -y
                pip install django==3.2 
                pip install django-widget-tweaks
                pip install pillow
                sudo apt install unzip -y 
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                unzip awscliv2.zip
                sudo ./aws/install
                mkdir app
                cd app
                aws s3 cp s3://my-unique-artifactory/ . --recursive
                python3 manage.py runserver 0.0.0.0:8000
                """)
        ami_map = {
        'ap-south-1': 'ami-08e5424edfe926b43'
}
        # Creates an EC2 instance
        instance = ec2.Instance(
            self, "AppInstance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.generic_linux(ami_map),
            vpc=vpc,
            security_group=instance_sg,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            role=instance_role, #Assign the IAM role to the instance
            user_data = user_data
        )


        
        
 