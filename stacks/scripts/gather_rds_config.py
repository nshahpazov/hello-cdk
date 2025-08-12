import json

from datetime import datetime

import boto3


RDS_RESOURCE_TYPE = "AWS::RDS::DBInstance"


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


def get_rds_config(rdsname):
    rdsclient = boto3.client("rds")
    res = rdsclient.describe_db_instances(DBInstanceIdentifier=rdsname)
    return res["DBInstances"][0]


def get_rds_parameters(rdsparamgroups):
    result = []
    rdsclient = boto3.client("rds")

    for i in rdsparamgroups:
        name = i["DBParameterGroupName"]
        res = rdsclient.describe_db_parameters(DBParameterGroupName=name)
        x = {"DBParamGroup": i, "Parameters": res["Parameters"]}
        result.append(x)

    return result


def find_rds_resource(res):
    resources_list = json.loads(res["Resourceslist"])
    for resource in resources_list:
        if resource["Type"] == "AWS::RDS::DBInstance":
            return resource["PhysicalResourceId"]
    return None


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
    param = None
    result = {}

    rdsrsname = find_rds_resource(event)
    rdsconfig = get_rds_config(rdsrsname)

    if len(rdsconfig["DBParameterGroups"]) > 0:
        param = get_rds_parameters(rdsconfig["DBParameterGroups"])

    result["Result"] = json.dumps(
        {"config": json.loads(json.dumps(rdsconfig, default=myconverter)), "parameters": param}
    )

    return result


if __name__ == "__main__":
    # load resources from json file
    # Test the function with a sample ARN
    with open("resources_list.json") as f:
        resources = json.load(f)

    event = {
        "Resourceslist": resources,
    }

    print(handler(event, None))
