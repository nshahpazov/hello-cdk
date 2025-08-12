import json

from datetime import datetime, timedelta

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


def get_related_metrics(res):
    cwclient = boto3.client("cloudwatch", region_name=res["Region"])

    response = cwclient.list_metrics(
        Namespace="AWS/ECS",
        Dimensions=[
            {"Name": "ServiceName", "Value": res["ServiceName"]},
            {"Name": "ClusterName", "Value": res["ClusterName"]},
        ],
    )
    return response["Metrics"]


def get_stat(res, metricname, stat):
    cwclient = boto3.client("cloudwatch", region_name=res["Region"])

    response = cwclient.get_metric_statistics(
        Namespace="AWS/ECS",
        MetricName=metricname,
        StartTime=datetime.now() - timedelta(minutes=6),
        EndTime=datetime.now(),
        Period=1,
        Dimensions=[
            {"Name": "ServiceName", "Value": res["ServiceName"]},
            {"Name": "ClusterName", "Value": res["ClusterName"]},
        ],
        Statistics=[stat],
    )

    x = []
    result = {}
    if len(response["Datapoints"]) > 0:
        for i in response["Datapoints"]:
            x.append(i[stat])
        result["OverallValue"] = cal_average(x)
    else:
        result["OverallValue"] = None
    result["Statistics"] = stat
    result["TimeWindow"] = 60
    # result['Datapoints'] = response['Datapoints']
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
    result = {}

    if arn is not None:
        ecsservice = arn_deconstruct(arn)
        result = {}
        output = {}
        result["CPUUtilization"] = get_stat(ecsservice, "CPUUtilization", "Maximum")
        result["MemoryUtilization"] = get_stat(ecsservice, "MemoryUtilization", "Maximum")
        serialized_result = json.dumps(result, default=myconverter)
        result = json.loads(serialized_result)
        output["Result"] = json.dumps(result)

    result = output

    return result
