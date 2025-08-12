from __future__ import annotations

import json

from dataclasses import dataclass

import boto3


def get_arn_details_from_arn(arn: str) -> ArnDetails:
    # arn:aws:cloudwatch:us-east-1:754323466686:alarm:mysecretword-canary-alarm
    service, region, account_id, service_type, name = arn.split(":")[2:7]

    # second version
    return ArnDetails(
        service=service,
        region=region,
        account_id=account_id,
        service_type=service_type,
        name=name,
    )


def locate_alarm_triggerer(alarm: ArnDetails) -> ArnDetails | None:
    cwclient = boto3.client("cloudwatch", region_name=alarm.region)

    alarm_detail = cwclient.describe_alarms(AlarmNames=[alarm.name])

    if len(alarm_detail["MetricAlarms"]) <= 0:
        return None

    metric_alarm = alarm_detail["MetricAlarms"][0]
    namespace = metric_alarm["Namespace"]

    # Condition if NameSpace is CloudWatch Syntetics
    if namespace != "CloudWatchSynthetics" or "Dimensions" not in metric_alarm:
        return None

    dimensions = metric_alarm["Dimensions"]

    for dimension in dimensions:
        if dimension["Name"] != "CanaryName":
            continue

        return ArnDetails(
            service=alarm.service,
            region=alarm.region,
            account_id=alarm.account_id,
            service_type=metric_alarm["Namespace"],
            name=dimension["Value"],
        )

    return None


def locate_canary_endpoint(canaryname, region):
    synclient = boto3.client("synthetics", region_name=region)
    canary = synclient.get_canary(Name=canaryname)["Canary"]

    if "Tags" in canary and "TargetEndpoint" in canary["Tags"]:
        return canary["Tags"]["TargetEndpoint"]
    return None


def locate_app_tag_value(resource: ArnDetails) -> str | None:

    if resource.service_type != "CloudWatchSynthetics":
        return None

    synclient = boto3.client("synthetics", region_name=resource.region)
    canary = synclient.get_canary(Name=resource.name)["Canary"]

    if "Tags" in canary and "Application" in canary["Tags"]:
        return canary["Tags"]["Application"]
    return None


def locate_app_resources_by_tag(tag, region):
    result = None

    # Search CloufFormation Stacks for tag
    cfnclient = boto3.client("cloudformation", region_name=region)
    stacks_list = cfnclient.list_stacks(
        StackStatusFilter=[
            "CREATE_COMPLETE",
            "ROLLBACK_COMPLETE",
            "UPDATE_COMPLETE",
            "UPDATE_ROLLBACK_COMPLETE",
            "IMPORT_COMPLETE",
            "IMPORT_ROLLBACK_COMPLETE",
        ]
    )
    for stack in stacks_list["StackSummaries"]:
        app_resources_list = []
        stack_name = stack["StackName"]
        stack_details = cfnclient.describe_stacks(StackName=stack_name)
        stack_info = stack_details["Stacks"][0]

        if "Tags" not in stack_info:
            continue
        for t in stack_info["Tags"]:
            # TODO: this should be changed to Application
            if not (t["Key"] == "Name" and t["Value"] == tag):
                continue
            app_resources = cfnclient.describe_stack_resources(
                StackName=stack_info["StackName"],
            )
            for resource in app_resources["StackResources"]:
                app_resources_list.append(
                    {
                        "PhysicalResourceId": resource["PhysicalResourceId"],
                        "Type": resource["ResourceType"],
                    }
                )
            result = app_resources_list

    return result


def handler(event, context):
    result = {}
    arn = event["CloudWatchAlarmARN"]
    alarm_details = get_arn_details_from_arn(arn)

    triggerer_details = locate_alarm_triggerer(alarm_details)
    tag_value = locate_app_tag_value(triggerer_details)  # Identify tag from source

    if triggerer_details is None or triggerer_details.service_type != "CloudWatchSynthetics":
        return None

    endpoint = locate_canary_endpoint(
        triggerer_details.name,
        triggerer_details.region,
    )
    result["CanaryEndpoint"] = endpoint

    # Locate cloudformation with tag
    resources = locate_app_resources_by_tag(tag_value, alarm_details.region)
    result["ApplicationStackResources"] = json.dumps(resources)

    return result


@dataclass
class ArnDetails:
    """
    Class to hold the details of the ARN.
    """

    service: str
    region: str
    account_id: str
    service_type: str
    name: str


if __name__ == "__main__":
    # Test the function with a sample ARN
    test_event = {
        "CloudWatchAlarmARN": "arn:aws:cloudwatch:eu-central-1:556318972711:alarm:ApplicationStack-CanaryMonitorCanaryDurationAlarmC33CD9BB-vME7xScGCbs8"
    }
    result = handler(test_event, None)

    # save to json file
    with open("resources_list.json", "w") as outfile:
        json.dump(result["ApplicationStackResources"], outfile, indent=4)
