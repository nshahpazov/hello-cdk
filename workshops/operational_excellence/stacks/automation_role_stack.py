from __future__ import annotations

from attr import dataclass
from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from constructs import Construct


class AutomationRoleStack(Stack):
    """
    A stack for the automation role
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.role = iam.Role(
            scope=self,
            id="AutomationRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ssm.amazonaws.com"),
                iam.ServicePrincipal("ec2.amazonaws.com"),
            ),
            description="Automation role for the EC2 instance",
            role_name="AutomationRole",
            path="/",
        )

        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                # this is not a good practice, but for the sake of the workshop
                resources=["*"],
            )
        )

        # this is used with the AWS-PublishSNSNotification SSM Automation document to send notifications on SNS.
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["sns:Publish"],
                # this is not a good practice, but for the sake of the workshop
                resources=["*"],
            )
        )

        managed_policy_arns = [
            "arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole",
            "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess",
            "arn:aws:iam::aws:policy/CloudWatchLogsReadOnlyAccess",
            "arn:aws:iam::aws:policy/AmazonRDSReadOnlyAccess",
            "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess",
            "arn:aws:iam::aws:policy/AmazonECS_FullAccess",
            "arn:aws:iam::aws:policy/CloudWatchSyntheticsReadOnlyAccess",
        ]

        for policy_arn in managed_policy_arns:
            self.role.add_managed_policy(
                iam.ManagedPolicy.from_managed_policy_arn(
                    self, policy_arn.rsplit("/", maxsplit=1)[-1], policy_arn
                )
            )

    @property
    def role_arn(self) -> str:
        """Returns the role ARN"""
        return self.role.role_arn
