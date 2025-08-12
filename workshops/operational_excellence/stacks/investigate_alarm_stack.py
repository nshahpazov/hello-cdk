from pathlib import Path

from aws_cdk import Stack
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class InvestigateAlarmStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, iam_role_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        document_name = "Playbook-Investigate-Application-Resources"

        def load_script(filename: str) -> str:
            return Path(f"stacks/scripts/{filename}").read_text(encoding="utf-8")

        # Load scripts from files
        scripts = {
            "Gather_ELB_Statistics": load_script("gather_elb_statistics.py"),
            "Gather_RDS_Config": load_script("gather_rds_config.py"),
            "Gather_RDS_Statistics": load_script("gather_rds_statistics.py"),
            "Gather_ECS_Statistics": load_script("gather_ecs_statistics.py"),
            "Gather_ECS_Error_Logs": load_script("gather_ecs_error_logs.py"),
            "Gather_ECS_Config": load_script("gather_ecs_config.py"),
            "Inspect_Playbook_Results": load_script("inspect_playbook_results.py"),
        }

        # Define main steps
        main_steps = []
        for step_name, script_content in scripts.items():
            main_steps.append(
                {
                    "name": step_name,
                    "action": "aws:executeScript",
                    "description": step_name.replace("_", " "),
                    "outputs": [
                        {
                            "Name": "Result",
                            "Selector": "$.Payload.Result",
                            "Type": "String",
                        }
                    ],
                    "inputs": {
                        "Runtime": "python3.11",
                        "Handler": "handler",
                        "InputPayload": (
                            {"Resourceslist": "{{Resources}}"}
                            if not step_name.startswith("Inspect")
                            else {
                                "ELBStatistics": "{{Gather_ELB_Statistics.Result}}",
                                "RDSConfig": "{{Gather_RDS_Config.Result}}",
                                "RDSStatistics": "{{Gather_RDS_Statistics.Result}}",
                                "ECSStatistics": "{{Gather_ECS_Statistics.Result}}",
                                "ECSErrorLogs": "{{Gather_ECS_Error_Logs.Result}}",
                                "ECSConfig": "{{Gather_ECS_Config.Result}}",
                            }
                        ),
                        "Script": script_content,
                    },
                }
            )

        # Create the SSM Automation Document
        ssm.CfnDocument(
            self,
            "InvestigateAlarmSSMDocument",
            document_type="Automation",
            name=document_name,
            content={
                "schemaVersion": "0.3",
                "assumeRole": "{{AutomationAssumeRole}}",
                "parameters": {
                    "Resources": {
                        "type": "String",
                        "description": "(Required) The Stringified Resources list from Gather Resource Alarm Output.",
                    },
                    "AutomationAssumeRole": {
                        "type": "String",
                        "default": iam_role_arn,
                        "description": "(Optional) IAM role ARN for Automation",
                    },
                },
                "outputs": ["Inspect_Playbook_Results.Result"],
                "mainSteps": main_steps,
            },
        )
