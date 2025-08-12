from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_sns as sns
from aws_cdk import aws_ssm as ssm
from constructs import Construct


APPROVAL_GATE_DOCUMENT_DESCRIPTION = """
This document is used to create an approval gate for the automation process.
The approval gate is a manual step that requires user input to proceed with the automation.
The document uses the AWS Systems Manager Automation service to create the approval gate.
The approval gate is created using the AWS-CreateApprovalGate document, which is a built-in Systems Manager Automation document.
The approval gate is created in the specified region and is associated with the specified SNS topic.
The approval gate is created using the AWS-CreateApprovalGate document, which is a built-in Systems Manager Automation document.
"""


RUN_AUTO_APPROVE_SCRIPT = """
import boto3

def handler(event, context):
    client = boto3.client('ssm')
    client.start_automation_execution(
        DocumentName='ApprovalTimer',
        Parameters={
            'Timer': [ event['Timer'] ],
            'AutomationExecutionId' : [ event['AutomationExecutionId'] ]
        }
    )
    return None
"""


class ApprovalGateStack(Stack):
    """
    This class represents the Approval Gate stack in the AWS CloudFormation template.
    It is responsible for creating the necessary resources for the approval gate process.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        iam_role_arn: str,
        topic_arn: str,
        **kwargs,
    ) -> None:
        """
        Initialize the ApprovalGateStack.

        :param scope: The scope in which this stack is defined.
        :param id: The ID of the stack.
        :param iam_role_arn: The ARN of the IAM role to assume for the automation.
        :param topic_arn: The ARN of the SNS topic to send notifications to.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(scope, construct_id, **kwargs)

        self.iam_role_arn = iam_role_arn
        self.topic_arn = topic_arn

        self.approval_timer = self.create_approval_timer()
        self.approval_gate = self.create_approval_gate()

    def create_approval_timer(self) -> ssm.CfnDocument:
        return ssm.CfnDocument(
            scope=self,
            id="ApprovalTimer",
            document_type="Automation",
            name="ApprovalTimer",
            content={
                "schemaVersion": "0.3",
                "description": APPROVAL_GATE_DOCUMENT_DESCRIPTION,
                "assumeRole": "{{AutomationAssumeRole}}",
                "parameters": {
                    "AssumedRoleArn": {
                        "type": "String",
                        "description": "The ARN of the role to assume for the automation.",
                        "default": self.iam_role_arn,
                    },
                    "Timer": {
                        "type": "String",
                        "description": "The duration of the approval timer.",
                        "default": "PT5M",  # 5 minutes
                    },
                    "AutomationExecutionId": {
                        "type": "String",
                        "description": "The ID of the automation execution.",
                        "default": "{{automation:EXECUTION_ID}}",
                    },
                },
                # Add more content as needed
                "mainSteps": [
                    {
                        "name": "ApprovalTimer",
                        "action": "aws:sleep",
                        "inputs": {
                            "Duration": "{{Timer}}",
                        },
                    },
                    {
                        "name": "ApproveExecution",
                        "action": "aws:executeAwsApi",
                        "inputs": {
                            "Api": "SendAutomationSignal",
                            "Service": "ssm",
                            "Payload": {
                                "Comment": ["Automatic Approved by Automatic-Approval-With-Timer"]
                            },
                            "AutomationExecutionId": "{{AutomationExecutionId}}",
                            "SignalType": "Approve",
                        },
                    },
                ],
            },
        )

    def create_approval_gate(self) -> ssm.CfnDocument:
        return ssm.CfnDocument(
            scope=self,
            id="ApprovalGateWithTimer",
            document_type="Automation",
            name="Approval-Gate",
            content={
                "schemaVersion": "0.3",
                "assumeRole": self.iam_role_arn,
                "parameters": {
                    "Timer": {"type": "String", "default": "PT10M"},
                    "NotificationTopicArn": {"type": "String"},
                    "NotificationMessage": {"type": "String"},
                    "ApproverArn": {"type": "String"},
                },
                "outputs": ["getApprovalStatus.approvalStatusVariable"],
                "mainSteps": [
                    {
                        "name": "executeAutoApproveTimer",
                        "action": "aws:executeScript",
                        "inputs": {
                            "Runtime": "python3.11",
                            "Handler": "handler",
                            "InputPayload": {
                                "AutomationExecutionId": "{{automation:EXECUTION_ID}}",
                                "Timer": "{{Timer}}",
                            },
                            # this is done in the background using boto3 ssm client
                            # to start the automation execution for the approval timer
                            "Script": RUN_AUTO_APPROVE_SCRIPT,
                        },
                    },
                    {
                        "name": "ApproveOrDeny",
                        "action": "aws:approve",
                        "onFailure": "Continue",
                        "isCritical": False,
                        "inputs": {
                            "NotificationArn": "{{NotificationTopicArn}}",
                            "Message": "{{NotificationMessage}}",
                            "MinRequiredApprovals": 1,
                            "Approvers": ["{{ApproverArn}}", self.iam_role_arn],
                        },
                    },
                    {
                        "name": "getApprovalStatus",
                        "action": "aws:executeAwsApi",
                        "maxAttempts": 1,
                        "inputs": {
                            "Service": "ssm",
                            "Api": "DescribeAutomationStepExecutions",
                            "AutomationExecutionId": "{{automation:EXECUTION_ID}}",
                            "Filters": [{"Key": "StepName", "Values": ["requestApproval"]}],
                        },
                        "outputs": [
                            {
                                "Name": "approvalStatusVariable",
                                "Selector": "$.StepExecutions[0].Outputs.ApprovalStatus[0]",
                                "Type": "String",
                            }
                        ],
                    },
                ],
            },
        )
