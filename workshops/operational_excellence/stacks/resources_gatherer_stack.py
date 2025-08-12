from aws_cdk import Stack
from aws_cdk import aws_ssm as ssm

# we can have automation documents in the same stack as the application stack
# from cdk_ssm_documents import AutomationDocument
from constructs import Construct


class ResourcesGathererStack(Stack):
    """
    Gather resources related to the CloudWatch Alarm.
    This stack creates an SSM document that can be used to gather resources related to the CloudWatch Alarm.
    The SSM document is used by the Automation service to execute the script that gathers the resources.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        assumed_role_arn: str,
        canary_duration_alarm_arn: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # Load the entire script as a string
        with open(
            "workshops/operational_excellence/stacks/scripts/gather_app_resources.py",
            "r",
        ) as f:
            script_content = f.read()

        # Build the SSM document
        ssm.CfnDocument(
            self,
            "PlaybookGatherAppResourceAlarm",
            name="Playbook-Gather-Resources5",
            document_type="Automation",
            content={
                "schemaVersion": "0.3",
                "assumeRole": "{{AutomationAssumeRole}}",
                "parameters": {
                    "AlarmARN": {
                        "type": "String",
                        "default": canary_duration_alarm_arn,
                        "description": "(Required) The ARN of the CloudWatch Alarm to gather resources for.",
                    },
                    "AutomationAssumeRole": {
                        "type": "String",
                        "default": assumed_role_arn,
                        "description": "(Optional) The ARN of the role that allows Automation to perform the actions on your behalf.",
                    },
                },
                "outputs": ["Gather_Resources_For_Alarm.Resources"],
                "mainSteps": [
                    {
                        "name": "Gather_Resources_For_Alarm",
                        "action": "aws:executeScript",
                        "description": "Gather AWS resources related to the Alarm, based on its Tag",
                        "inputs": {
                            "Runtime": "python3.11",
                            "Handler": "handler",
                            "InputPayload": {"CloudWatchAlarmARN": "{{AlarmARN}}"},
                            "Script": script_content,
                        },
                        "outputs": [
                            {
                                "Name": "Resources",
                                "Selector": "$.Payload.ApplicationStackResources",
                                "Type": "String",
                            }
                        ],
                    }
                ],
            },
        )
