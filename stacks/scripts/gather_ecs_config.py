import json

from datetime import datetime

import boto3


def arn_deconstruct(arn):
    arnlist = arn.split(":")

    service = arnlist[2]
    region = arnlist[3]
    accountid = arnlist[4]
    resources = arnlist[5].split("/")
    servicetype = resources[0]
    clustername = resources[1]
    servicename = resources[2]

    return {
        "Service": service,
        "Region": region,
        "AccountId": accountid,
        "Type": servicetype,
        "ClusterName": clustername,
        "ServiceName": servicename,
    }


def get_ecs_service_config(res):
    ecsclient = boto3.client("ecs")

    response = ecsclient.describe_services(
        cluster=res["ClusterName"], services=[res["ServiceName"]]
    )

    if len(response["services"]) > 0:
        result = response["services"][0]

    return result


def get_scaling_policy(res):
    result = []
    aaclient = boto3.client("application-autoscaling")

    response = aaclient.describe_scaling_policies(
        ServiceNamespace="ecs",
        ResourceId="service/{}/{}".format(res["ClusterName"], res["ServiceName"]),
    )

    if len(response["ScalingPolicies"]) > 0:
        result = response["ScalingPolicies"]

    return result


def find_ecsservice_resource(res):
    result = None
    r = json.loads(res["Resourceslist"])
    for i in r:
        if i["Type"] == "AWS::ECS::Service":
            result = i["PhysicalResourceId"]
    return result


def cal_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t

    avg = sum_num / len(num)
    return avg


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


def handler(event, context):

    arn = find_ecsservice_resource(event)
    ecsres = arn_deconstruct(arn)
    result = {}
    output = {}

    if ecsres is not None:
        ecssvccfg = json.dumps(get_ecs_service_config(ecsres), default=myconverter)

    result = json.loads(ecssvccfg)
    result["scalingpolicies"] = json.loads(
        json.dumps(get_scaling_policy(ecsres), default=myconverter)
    )

    output["Result"] = json.dumps(result, default=myconverter)
    return output
