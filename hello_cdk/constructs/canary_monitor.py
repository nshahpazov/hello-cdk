"""
This module contains the CanaryMonitor construct.
"""

from pathlib import Path

from aws_cdk import Duration, Tags
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_cloudwatch_actions as cw_actions
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from aws_cdk import aws_synthetics as synthetics
from aws_cdk.aws_sns_subscriptions import EmailSubscription
from constructs import Construct


class CanaryMonitor(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        alb_dns_name: str,
        security_group_id: str,
        private_subnet_ids: list[str],
        **kwargs,
    ) -> None:
        """
        A construct for the CanaryMonitor encapsulating the canary monitor
        and the SNS topic for alerts.
        It contains the following resources:
        1. S3 bucket for storing canary results
        2. IAM role for the canary
        """
        super().__init__(scope, id, **kwargs)

        results_bucket = s3.Bucket(
            scope=self,
            id="ResultsBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=None,
        )

        self.set_role()

        results_bucket.grant_read_write(self.canary_role)

        canary_script = Path(
            "hello_cdk/constructs/scripts/canary-script.js",
        ).read_text(encoding="utf-8")

        self.security_group = ec2.SecurityGroup.from_security_group_id(
            scope=self,
            id="CanarySecurityGroup",
            security_group_id=security_group_id,
        )

        Tags.of(self.security_group).add("Name", "Canary-SG")
        Tags.of(self.security_group).add("Application", "OpsExcellence-Lab")

        # create the canary monitor
        canary = synthetics.Canary(
            scope=self,
            id="Canary",
            canary_name="my-secret-word-canary",
            role=self.canary_role,
            # test is the test that the canary will run against the application
            test=synthetics.Test.custom(
                code=synthetics.Code.from_inline(canary_script),
                handler="index.handler",
            ),
            runtime=synthetics.Runtime.SYNTHETICS_NODEJS_PUPPETEER_7_0,
            environment_variables={"APP_ENDPOINT": alb_dns_name},
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnets=[
                    ec2.Subnet.from_subnet_id(self, f"PrivateSubnet{i+1}", private_subnet_ids[i])
                    for i in range(2)
                ],
            ),
            schedule=synthetics.Schedule.rate(Duration.minutes(1)),
            start_after_creation=True,
            artifacts_bucket_location=synthetics.ArtifactsBucketLocation(
                bucket=results_bucket,
                prefix="canary-results",
            ),
            security_groups=[self.security_group],
            success_retention_period=Duration.days(30),
            failure_retention_period=Duration.days(30),
        )

        Tags.of(canary).add("Application", "OpsExcellence-Lab")
        Tags.of(canary).add("TargetEndpoint", alb_dns_name)

        self._canary_duration_alarm = cloudwatch.Alarm(
            scope=self,
            id="CanaryDurationAlarm",
            metric=canary.metric_duration(
                period=Duration.minutes(1),
                statistic="avg",
            ),
            # 100 means 100ms=0.1s
            threshold=100,
            evaluation_periods=1,
            datapoints_to_alarm=1,
        )

        system_event_topic = sns.Topic(scope=self, id="SystemEventTopic")
        system_owner_topic = sns.Topic(scope=self, id="SystemOwnerTopic")

        system_event_topic.add_subscription(EmailSubscription("nshahpazov@gmail.com"))
        system_owner_topic.add_subscription(EmailSubscription("nshahpazov@gmail.com"))

        self._canary_duration_alarm.add_alarm_action(cw_actions.SnsAction(topic=system_event_topic))

    @property
    def canary_duration_alarm(self) -> cloudwatch.IAlarm:
        """Returns the canary duration alarm"""
        return self._canary_duration_alarm

    def set_role(self) -> None:
        """
        Adds the IAM role for the canary.
        The role has the following policies:
        1. S3 read/write
        2. CloudWatch logs
        3. CloudWatch alarms
        """
        self.canary_role = iam.Role(
            scope=self,
            id="CloudWatchSyntheticsRole",
            # 'assumed by' means what kind of services can assume this role
            # in this case, it is assumed by the lambda service
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="CloudWatch Synthetics lambda execution role for canary",
        )

        # we describe the policy for the canary role
        self.canary_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                    "s3:GetBucketLocation",
                    "s3:ListAllMyBuckets",
                    "s3:ListBucket",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:CreateLogGroup",
                    "cloudwatch:PutMetricData",
                    "ec2:*",
                    "ec2:CreateNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface",
                    "ec2:DescribeSecurityGroups",
                ],
                resources=["*"],
            )
        )
