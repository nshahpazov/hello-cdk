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
    servicemode = resources[1]
    resourcename = resources[2]
    resourceid = resources[3]

    return {
        "Service": service,
        "Region": region,
        "AccountId": accountid,
        "Type": servicetype,
        "Mode": servicemode,
        "Name": resourcename,
        "Id": resourceid,
    }


def get_related_metrics(elb):
    cwclient = boto3.client("cloudwatch", region_name=elb["Region"])
    if elb["Mode"] == "app":
        response = cwclient.list_metrics(
            Namespace="AWS/ApplicationELB",
            Dimensions=[
                {
                    "Name": "LoadBalancer",
                    "Value": "{}/{}/{}".format(elb["Mode"], elb["Name"], elb["Id"]),
                }
            ],
        )
    return response["Metrics"]


def get_stat(elb, metricname, stat):
    cwclient = boto3.client("cloudwatch", region_name=elb["Region"])

    if elb["Mode"] == "app":
        response = cwclient.get_metric_statistics(
            Namespace="AWS/ApplicationELB",
            MetricName=metricname,
            StartTime=datetime.now() - timedelta(minutes=60),
            EndTime=datetime.now(),
            Period=60,
            Dimensions=[
                {
                    "Name": "LoadBalancer",
                    "Value": "{}/{}/{}".format(elb["Mode"], elb["Name"], elb["Id"]),
                }
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
    return result


def find_elb_resource(res):
    result = None
    r = json.loads(res["Resourceslist"])
    for i in r:
        if i["Type"] == "AWS::ElasticLoadBalancingV2::Listener":
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

    arn = find_elb_resource(event)
    result = {}

    if arn is not None:
        elb = arn_deconstruct(arn)

        metricslist = get_related_metrics(elb)
        result["TargetResponseTime"] = get_stat(elb, "TargetResponseTime", "Average")
        result["Target2XXCount"] = get_stat(elb, "HTTPCode_Target_2XX_Count", "Sum")
        result["Target3XXCount"] = get_stat(elb, "HTTPCode_Target_2XX_Count", "Sum")
        result["Target4XXCount"] = get_stat(elb, "HTTPCode_Target_4XX_Count", "Sum")
        result["Target5XXCount"] = get_stat(elb, "HTTPCode_Target_5XX_Count", "Sum")
        result["TargetConnectionErrorCount"] = get_stat(elb, "TargetConnectionErrorCount", "Sum")
        result["UnHealthyHostCount"] = get_stat(elb, "UnHealthyHostCount", "Average")
        result["ActiveConnectionCount"] = get_stat(elb, "ActiveConnectionCount", "Sum")
        result["ELB3XXCount"] = get_stat(elb, "HTTPCode_ELB_3XX_Count", "Sum")
        result["ELB4XXCount"] = get_stat(elb, "HTTPCode_ELB_4XX_Count", "Sum")
        result["ELB5XXCount"] = get_stat(elb, "HTTPCode_ELB_5XX_Count", "Sum")
        result["ELB500Count"] = get_stat(elb, "HTTPCode_ELB_500_Count", "Sum")
        result["ELB502Count"] = get_stat(elb, "HTTPCode_ELB_502_Count", "Sum")
        result["ELB503Count"] = get_stat(elb, "HTTPCode_ELB_503_Count", "Sum")
        result["ELB504Count"] = get_stat(elb, "HTTPCode_ELB_504_Count", "Sum")

        serialized_result = json.dumps(result, default=myconverter)
        result["Result"] = json.dumps(json.loads(serialized_result))

    return result
