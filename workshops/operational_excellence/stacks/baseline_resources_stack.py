import aws_cdk as core

from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from constructs import Construct

from .constructs.vpc import VPC


class BaselineResourcesStack(Stack):
    """
    This stack is used to create the baseline resources for the Op Exc.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        vpc_configuration = VPC(
            scope=self,
            construct_id="VPC",
        )

        # ecr repository is used for storing the application container image
        ecr_repository = ecr.Repository(
            scope=self,
            id="ECRRepository",
            repository_name="hello-cdk",
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=3,
                )
            ],
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        core.CfnOutput(
            self,
            "CanarySGId",
            value=vpc_configuration.canary_security_group.security_group_id,
            export_name="BaselineResourcesStack-CanarySGId",
        )

        core.CfnOutput(
            self,
            "BaselineVpcStack",
            description="Baseline VPC",
            value=vpc_configuration.vpc_id,
            export_name="BaselineVpcStack",
        )

        core.CfnOutput(
            self,
            "OutputVPCCidrBlock",
            description="Baseline VPC Cidr Block",
            value=vpc_configuration.vpc_cidr_block,
            export_name=f"{self.stack_name}-VpcCidrBlock",
        )

        # output availability zones
        core.CfnOutput(
            self,
            "OutputAZs",
            description="Availability Zones",
            value=",".join(vpc_configuration.availability_zones or []),
            export_name="OutputAZs",
        )

        core.CfnOutput(
            self,
            "OutputPublicSubnet1",
            description="Public Subnet 1 VPC",
            value=vpc_configuration.public_subnets[0].subnet_id,
            export_name="PublicSubnet1",
        )

        core.CfnOutput(
            self,
            "OutputPublicSubnet2",
            description="Public Subnet 2 VPC",
            value=vpc_configuration.public_subnets[1].subnet_id,
            export_name="PublicSubnet2",
        )

        core.CfnOutput(
            self,
            "OutputPrivateSubnet1",
            description="Private Subnet 1 VPC",
            value=vpc_configuration.private_subnets[0].subnet_id,
            export_name="PrivateSubnet1",
        )

        core.CfnOutput(
            self,
            "OutputPrivateSubnet2",
            description="Private Subnet 2 VPC",
            value=vpc_configuration.private_subnets[1].subnet_id,
            export_name="PrivateSubnet2",
        )

        core.CfnOutput(
            self,
            "OutputAppContainerRepository",
            description="Application ECR Repository",
            value=ecr_repository.repository_name,
            export_name=f"{self.stack_name}-AppContainerRepository",
        )

        core.CfnOutput(
            self,
            "PublicSubnet1RouteTable",
            description="Public Subnet 1 Route Table",
            value=vpc_configuration.public_route_table_ids[0],
            export_name="PublicSubnet1RouteTable",
        )
        core.CfnOutput(
            self,
            "PublicSubnet2RouteTable",
            description="Public Subnet 2 Route Table",
            value=vpc_configuration.public_route_table_ids[1],
            export_name="PublicSubnet2RouteTable",
        )

        core.CfnOutput(
            self,
            "PrivateSubnet1RouteTable",
            description="Private Subnet 1 Route Table",
            value=vpc_configuration.private_route_table_ids[0],
            export_name="PrivateSubnet1RouteTable",
        )

        core.CfnOutput(
            self,
            "PrivateSubnet2RouteTable",
            description="Private Subnet 2 Route Table",
            value=vpc_configuration.private_route_table_ids[1],
            export_name="PrivateSubnet2RouteTable",
        )
