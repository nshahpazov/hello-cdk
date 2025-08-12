from __future__ import annotations

import aws_cdk as core

from aws_cdk import Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk.aws_ec2 import IVpc
from constructs import Construct


class LoadBalancer(Construct):
    """
    Load Balancer construct for the application.
    """

    def __init__(self, scope: Construct, id: str, vpc: IVpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.security_group = LoadBalancer.create_security_group(self, vpc)
        self.load_balancer = self.create_load_balancer(vpc, self.security_group)

        Tags.of(self.load_balancer).add("Name", "ALB")
        Tags.of(self.load_balancer).add("Application", "OpsExcellence-Lab")

        # listener is like a receptionist for the load balancer.
        # Without it, the load balancer doesn’t know what to do with incoming traffic.
        self.listener = self.load_balancer.add_listener("Listener", port=80, open=True)

        self.target_group = self.create_target_group(vpc)

        Tags.of(self.target_group).add("Name", "ALB-TargetGroup")
        Tags.of(self.target_group).add("Application", "OpsExcellence-Lab")
        Tags.of(self.security_group).add("Name", "ALB-SG")
        Tags.of(self.security_group).add("Application", "OpsExcellence-Lab")
        Tags.of(self.listener).add("Name", "ALB-Listener")
        Tags.of(self.listener).add("Application", "OpsExcellence-Lab")

        self.listener.add_target_groups(
            "AddTargetGroup",
            target_groups=[self.target_group],
        )

    @staticmethod
    def create_security_group(scope, vpc: IVpc) -> ec2.SecurityGroup:
        """
        Create a security group for the load balancer.
        This security group allows HTTP traffic from the internet.
        :param vpc: The VPC to associate the security group with.
        """
        alb_security_group = ec2.SecurityGroup(
            scope=scope,
            id="ALBSecurityGroup",
            vpc=vpc,
            description="Security group for ALB",
        )

        # Allow HTTP traffic from the internet
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic from the internet",
        )
        return alb_security_group

    def create_load_balancer(
        self,
        vpc: IVpc,
        security_group: ec2.SecurityGroup,
    ) -> elbv2.ApplicationLoadBalancer:
        """
        Create an Application Load Balancer (ALB).
        :param vpc: The VPC to associate the load balancer with.
        """

        # Load Balancer
        load_balancer = elbv2.ApplicationLoadBalancer(
            self,
            "ALB",
            vpc=vpc,
            security_group=security_group,
            internet_facing=True,
        )

        return load_balancer

    def create_target_group(
        self,
        vpc: IVpc,
    ) -> elbv2.ApplicationTargetGroup:
        """
        Create a target group for the load balancer.
        :param vpc: The VPC to associate the target group with.
        :return: The target group.
        """
        return elbv2.ApplicationTargetGroup(
            scope=self,
            id="MyTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            health_check=elbv2.HealthCheck(
                path="/health",  # Make sure your service exposes this path!
                interval=core.Duration.seconds(30),
            ),
            # since we are going to use ecs with fargate, we need to set the target type to IP
            # this means that the target group will use the IP address of the task
            target_type=elbv2.TargetType.IP,
        )
