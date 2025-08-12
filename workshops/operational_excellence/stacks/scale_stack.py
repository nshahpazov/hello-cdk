from aws_cdk import Stack
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class ScaleStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        iam_role_arn: str,
        ecs_service_name: str,
        ecs_cluster_name: str,
        topic_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ssm.CfnDocument(
            self,
            "RemediationPlaybook",
            document_type="Automation",
            name="Remediation-Scale-Up-On-Approval",
            content={
                "schemaVersion": "0.3",
                "assumeRole": iam_role_arn,
                "parameters": {
                    "Timer": {"type": "String", "default": "PT10M"},
                    "NotificationTopicArn": {
                        "type": "String",
                        "description": "The ARN of the SNS topic to send notifications to.",
                        "default": topic_arn,
                    },
                    "NotificationMessage": {"type": "String"},
                    "ApproverArn": {"type": "String"},
                    "ECSServiceName": {
                        "type": "String",
                        "description": "The name of the ECS service to scale up.",
                        "default": ecs_service_name,
                    },
                    "ECSDesiredCount": {"type": "String", "default": "2"},
                    "ECSClusterName": {
                        "type": "String",
                        "default": ecs_cluster_name,
                        "description": "The name of the ECS cluster.",
                    },
                },
                "mainSteps": [
                    {
                        "name": "ExecuteApprovalGateWithTimer",
                        "action": "aws:executeAutomation",
                        "outputs": [
                            {
                                "Name": "ApprovalStatus",
                                "Selector": "$.getApprovalStatus.approvalStatusVariable",
                                "Type": "String",
                            }
                        ],
                        "inputs": {
                            "DocumentName": "Approval-Gate",
                            "RuntimeParameters": {
                                "Timer": "{{Timer}}",
                                "NotificationTopicArn": "{{NotificationTopicArn}}",
                                "NotificationMessage": "{{NotificationMessage}}",
                                "ApproverArn": "{{ApproverArn}}",
                            },
                        },
                    },
                    {
                        "name": "CheckApprovalStatus",
                        "action": "aws:assertAwsResourceProperty",
                        "inputs": {
                            "PropertySelector": "$.ExecuteApprovalGateWithTimer.Output.ApprovalStatus",
                            "ExpectedValue": "Approved",
                        },
                    },
                    {
                        "name": "UpdateECSServiceDesiredCount",
                        "action": "aws:executeAwsApi",
                        "inputs": {
                            "Service": "ecs",
                            "Api": "UpdateService",
                            "service": "{{ECSServiceName}}",
                            "forceNewDeployment": True,
                            "desiredCount": "{{ECSDesiredCount}}",
                            "cluster": "{{ECSClusterName}}",
                        },
                    },
                ],
            },
        )
