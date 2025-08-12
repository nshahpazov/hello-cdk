from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class VPC(Construct):
    """
    This construct creates a VPC with 2 public and 2 private subnets.
    It also creates a NAT Gateway and an Internet Gateway.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.create_resources()

    def create_resources(self) -> None:
        """
        This method creates the VPC and its resources.
        """
        # create a VPC with 2 public and 2 private subnets

        public_subnet_configuration = ec2.SubnetConfiguration(
            name="Public",
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24,
        )

        private_subnet_configuration = ec2.SubnetConfiguration(
            name="Private1",
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            cidr_mask=24,
        )

        vpc = ec2.Vpc(
            self,
            "VPC",
            # cidr="172.31.0.0/16",
            # set availability zones to 2
            max_azs=2,
            # set the number of NAT gateways to 1. Nat Gateways are used to
            # allow instances in a private subnet to access the internet.
            nat_gateways=1,
            # set the number of public and private subnets to 2
            subnet_configuration=[
                public_subnet_configuration,
                private_subnet_configuration,
            ],
        )

        # create a security group for the canary
        self.canary_security_group = ec2.SecurityGroup(
            self,
            "CanarySecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
            description="Security group for the canary",
        )

        self.vpc_id = vpc.vpc_id
        self.availability_zones = vpc.availability_zones
        self.vpc_cidr_block = vpc.vpc_cidr_block
        self.public_subnets = vpc.public_subnets
        self.private_subnets = vpc.private_subnets
        self.internet_gateway_id = vpc.internet_gateway_id
        # set to self route table ids
        self.public_route_table_ids = [
            subnet.route_table.route_table_id for subnet in vpc.public_subnets
        ]
        self.private_route_table_ids = [
            subnet.route_table.route_table_id for subnet in vpc.private_subnets
        ]
