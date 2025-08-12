from __future__ import annotations

#
from attr import dataclass
from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_sns as sns
from aws_cdk import aws_ssm as ssm
from aws_cdk.aws_sns_subscriptions import EmailSubscription
from constructs import Construct


DESCRIPTION = """
## What does this playbook do?
This playbook will execute **Playbook-Gather-Resources** to gather Application resources monitored by a Canary.

Then subsequently execute **Playbook-Investigate-Application-Resources** to Investigate the resources for issues.
Outputs of the investigation will be sent to SNS Topic Subscriber.
## What are the inputs?
- **AlarmArn**: The ARN of the CloudWatch alarm that triggered
- **AssumedRoleArn**: The ARN of the role to assume for the automation
## What are the outputs?
- **Resources**: The resources that were gathered by the playbook
- **InvestigateResults**: The results of the investigation
## What are the steps?
1. Gather resources from the CloudWatch alarm
2. Investigate the resources
3. Send the results to the SNS topic
## What are the prerequisites?
- The role that is assumed must have the following permissions:
    - `ssm:StartAutomationExecution`
    - `ssm:DescribeAutomationExecutions`
    - `ssm:GetAutomationExecution`
    - `ssm:StopAutomationExecution`
    - `sns:Publish`

"""


class InvestigateAlarmMetaStack(Stack):
    """ """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        iam_role_arn: str,
        canary_duration_alarm_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create the SNS topic
        #  Not sure if I should reuse another topic from another stack
        self.investigation_topic = sns.Topic(
            self,
            "InvestigationTopic",
            topic_name="InvestigationTopic",
        )

        self.investigation_topic.add_subscription(EmailSubscription("nshahpazov@gmail.com"))

        ssm.CfnDocument(
            scope=self,
            id="InvestigateAlarmPlaybook",
            document_type="Automation",
            name="InvestigateAlarmPlaybook2",
            content={
                "schemaVersion": "0.3",
                "description": DESCRIPTION,
                "parameters": {
                    "AlarmARN": {
                        "type": "String",
                        "description": "The ARN of the CloudWatch alarm that triggered",
                        "default": canary_duration_alarm_arn,
                    },
                    "AssumedRoleArn": {
                        "type": "String",
                        "description": "The ARN of the role to assume for the automation",
                        "default": iam_role_arn,
                    },
                    "SNSTopicARN": {
                        "type": "String",
                        "description": "The ARN of the SNS topic to send the results to",
                        "default": self.investigation_topic.topic_arn,
                    },
                },
                "mainSteps": [
                    {
                        "name": "gatherResources",
                        "action": "aws:executeAutomation",
                        "inputs": {
                            "DocumentName": "Playbook-Gather-Resources5",
                            "RuntimeParameters": {
                                "AlarmARN": "{{AlarmARN}}",
                            },
                        },
                    },
                    {
                        "name": "InvestigateResources",
                        "action": "aws:executeAutomation",
                        "inputs": {
                            "DocumentName": "Playbook-Investigate-Application-Resources",
                            "RuntimeParameters": {
                                "Resources": "{{gatherResources.Output}}",
                            },
                        },
                    },
                    {
                        "name": "AWSPublishSNSNotification",
                        "action": "aws:executeAutomation",
                        "inputs": {
                            "DocumentName": "AWS-PublishSNSNotification",
                            "RuntimeParameters": {
                                "TopicArn": "{{SNSTopicARN}}",
                                "Message": "{{InvestigateResources.Output}}",
                            },
                        },
                    },
                ],
            },
        )
