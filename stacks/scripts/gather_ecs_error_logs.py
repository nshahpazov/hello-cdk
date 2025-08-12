import json
import time

from datetime import datetime

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

    return {
        "Service": service,
        "Region": region,
        "AccountId": accountid,
        "Type": servicetype,
        "Mode": servicemode,
        "Name": resourcename,
    }


def find_ecs_resource(res):
    result = {}

    r = json.loads(res["Resourceslist"])
    for i in r:
        if i["Type"] == "AWS::ECS::Cluster":
            result["ECSCluster"] = i["PhysicalResourceId"]
        if i["Type"] == "AWS::ECS::Service":
            result["ECSService"] = i["PhysicalResourceId"]

    return result


def find_ecs_logs(ecsclsname, ecssvcname, region):
    result = []

    ecsclient = boto3.client("ecs", region_name=region)
    ecssvcres = ecsclient.describe_services(cluster=ecsclsname, services=[ecssvcname])

    if len(ecssvcres["services"]) > 0:
        taskdef = ecssvcres["services"][0]["taskDefinition"]
        taskdefres = ecsclient.describe_task_definition(taskDefinition=taskdef)

        contdef = taskdefres["taskDefinition"]["containerDefinitions"]

        for i in contdef:
            result.append(i["logConfiguration"])

    return result


def find_error_in_logs(loglist):
    result = []
    loggroups = []
    logsclient = boto3.client("logs")

    for i in loglist:
        options = i["options"]
        if "awslogs-group" in options:
            loggroups.append(options["awslogs-group"])
            now = int(datetime.now().timestamp())

            res = logsclient.start_query(
                logGroupNames=loggroups,
                startTime=now - 3000,
                endTime=now,
                queryString='fields @message | filter @message like "Error:" | limit 5',
            )

            response = None
            while response == None or response["status"] == "Running":
                time.sleep(1)
                response = logsclient.get_query_results(queryId=res["queryId"])

            if "results" in response:
                if len(response["results"]) > 0:
                    for i in response["results"]:
                        for x in i:
                            if x["field"] == "@ptr":
                                pointer = x["value"]
                        recdetail = logsclient.get_log_record(logRecordPointer=pointer)

                        result.append(recdetail["logRecord"])

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
    result = {}
    x = []
    res = find_ecs_resource(event)
    ecssvc = arn_deconstruct(res["ECSService"])
    loglist = find_ecs_logs(res["ECSCluster"], ecssvc["Name"], ecssvc["Region"])

    x = find_error_in_logs(loglist)

    if len(x) > 0:
        result["Result"] = json.dumps(x)
    else:
        result["Result"] = "None"

    return result
