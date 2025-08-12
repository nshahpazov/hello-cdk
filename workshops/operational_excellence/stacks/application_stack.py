from __future__ import annotations

import aws_cdk as core

from attr import dataclass
from aws_cdk import Stack, Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_kms as kms

# we can have automation documents in the same stack as the application stack
# from cdk_ssm_documents import AutomationDocument
from constructs import Construct

from hello_cdk.constructs.canary_monitor import CanaryMonitor
from hello_cdk.constructs.ecs import ECS
from hello_cdk.constructs.load_balancer import LoadBalancer
from hello_cdk.constructs.rds import RDS


class ApplicationStack(Stack):
    """
    Application stack.
    TODO: Add more comments and docstrings
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # import constants from the baseline stack
        vpc_stack_id = core.Fn.import_value("BaselineVpcStack")
        azs = core.Fn.import_value("OutputAZs").split(",")
        public_subnet1 = core.Fn.import_value("PublicSubnet1")
        public_subnet2 = core.Fn.import_value("PublicSubnet2")
        private_subnet1 = core.Fn.import_value("PrivateSubnet1")
        private_subnet2 = core.Fn.import_value("PrivateSubnet2")
        security_group_id = core.Fn.import_value("BaselineResourcesStack-CanarySGId")
        ecr_repository_name = core.Fn.import_value("BaselineResourcesStack-AppContainerRepository")
        # this should come from the baseline stack. it's hardcoded here for now
        ecr_repository_name = "walab-ops-sample-application"

        # import the vpc from the baseline stack and create a vpc object
        # representing the vpc
        vpc = ec2.Vpc.from_vpc_attributes(
            scope=self,
            id="ImportedVPC",
            availability_zones=azs,
            vpc_id=vpc_stack_id,
            public_subnet_ids=[public_subnet1, public_subnet2],
            private_subnet_ids=[private_subnet1, private_subnet2],
            public_subnet_names=["Public1", "Public2"],
            private_subnet_names=["Private1", "Private2"],
            public_subnet_route_table_ids=[
                core.Fn.import_value("PublicSubnet1RouteTable"),
                core.Fn.import_value("PublicSubnet2RouteTable"),
            ],
            private_subnet_route_table_ids=[
                core.Fn.import_value("PrivateSubnet1RouteTable"),
                core.Fn.import_value("PrivateSubnet2RouteTable"),
            ],
        )

        # load balancer is used to distribute traffic to the ECS service
        load_balancer = LoadBalancer(
            scope=self,
            id="LoadBalancer",
            vpc=vpc,
        )

        rds = RDS(
            scope=self,
            id="RDS",
            vpc=vpc,
        )

        self.ecs_construct = ECS(
            scope=self,
            id="ECS",
            alb_security_group=load_balancer.security_group,
            alb_target_group=load_balancer.target_group,
            vpc=vpc,
            kms_key=kms.Key(  # type: ignore[assignment]
                scope=self,
                id="AppKmsKey",
                description=("KMS key for encrypting/decrypting data in the " "Node.js app"),
                enable_key_rotation=True,
                # Optional, nice to have for reference
                alias="alias/my-app-kms-key",
                # Careful: this will delete the key if stack is destroyed
                removal_policy=core.RemovalPolicy.DESTROY,
            ),
            ecr_repository_name=ecr_repository_name,
            rds_secret=rds.secret,
            db_host=rds.instance.db_instance_endpoint_address,
            db_port=rds.instance.db_instance_endpoint_port,
        )

        # add ingress rule to the rds security group to allow traffic from the ECS service to the RDS instance
        rds.security_group.add_ingress_rule(
            peer=self.ecs_construct.ecs_security_group,
            connection=ec2.Port.tcp(3306),
            description="Allow ECS service to access RDS MySQL",
        )

        self.canary_monitor = CanaryMonitor(
            scope=self,
            id="CanaryMonitor",
            vpc=vpc,
            security_group_id=security_group_id,
            alb_dns_name=load_balancer.load_balancer.load_balancer_dns_name,
            private_subnet_ids=[private_subnet1, private_subnet2],
        )

        Tags.of(self).add("Name", "OpsExcellence-Lab")

    @property
    def arns(self) -> ApplicationStackArns:
        """
        Returns the ARNs of the application stack resources.
        """
        return ApplicationStackArns(
            canary_duration_alarm_arn=self.canary_monitor.canary_duration_alarm.alarm_arn,
        )

    @property
    def ecs_service_name(self) -> str:
        """
        Returns the ECS service name.
        """
        return self.ecs_construct.fargate_service.service_name

    @property
    def ecs_cluster_name(self) -> str:
        """
        Returns the ECS cluster name.
        """
        return self.ecs_construct.cluster_name


@dataclass
class ApplicationStackArns:
    """
    Data class for the application stack ARNs.
    """

    canary_duration_alarm_arn: str


# next steps
# figure out the many requests with ab to the decrypt endpoint
# - add a runbook to the canary monitor to ask for permission for to restart/scale up the ECS service
#
"""
TODO:
- load test on the encrpt endpoint instead of the decrypt endpoint
- Split code into multiple files/constructs and functions
- Add tests for the constructs and the resources
- Add more comments and docstrings
- Add a docker container with a web server to the ECS service and push it to ECR. See where this should happen as code. Maybe in CI/CD pipeline of the repo/app?
- Enable cloud watch logging for the ECS service
"""
