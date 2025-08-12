"""
This module contains a construct for SSM Automation Document that should
"""

from aws_cdk import aws_ssm as ssm
from constructs import Construct


class AutomationDocument(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        runbook_content = {
            "schemaVersion": "0.3",
            "description": "My automation runbook using CDK",
            "parameters": {
                "InstanceId": {
                    "type": "String",
                    "description": "(Required) The instance ID",
                }
            },
            "mainSteps": [
                {
                    "name": "runShellScript",
                    "action": "aws:runCommand",
                    "inputs": {
                        "DocumentName": "AWS-RunShellScript",
                        "Parameters": {"commands": ["echo Hello from CDK!"]},
                        "InstanceIds": ["{{ InstanceId }}"],
                    },
                }
            ],
        }

        ssm.CfnDocument(
            self,
            "AutomationRunbook",
            document_type="Automation",
            content=runbook_content,
            name="MyAutomationRunbook",
            document_format="YAML",
            update_method="NewVersion",  # Requires CDK v2.94.0+
        )
