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


def get_related_metrics(rdsname):
    cwclient = boto3.client("cloudwatch")
    response = cwclient.list_metrics(
        Namespace="AWS/RDS", Dimensions=[{"Name": "DBInstanceIdentifier", "Value": rdsname}]
    )
    return response["Metrics"]


def get_stat(rdsname, metricname, stat):
    cwclient = boto3.client("cloudwatch")

    response = cwclient.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName=metricname,
        StartTime=datetime.now() - timedelta(minutes=60),
        EndTime=datetime.now(),
        Period=60,
        Dimensions=[{"Name": "DBInstanceIdentifier", "Value": rdsname}],
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


def find_rds_resource(res):
    result = None
    r = json.loads(res["Resourceslist"])
    for i in r:
        if i["Type"] == "AWS::RDS::DBInstance":
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
    param = None
    result = {}

    rdsrsname = find_rds_resource(event)
    metricslist = get_related_metrics(rdsrsname)

    result["BinLogDiskUsage"] = get_stat(rdsrsname, "BinLogDiskUsage", "Sum")
    result["BurstBalance"] = get_stat(rdsrsname, "BurstBalance", "Average")
    result["CPUUtilization"] = get_stat(rdsrsname, "CPUUtilization", "Average")
    result["CPUCreditUsage"] = get_stat(rdsrsname, "CPUCreditUsage", "Sum")
    result["CPUCreditBalance"] = get_stat(rdsrsname, "CPUCreditBalance", "Maximum")
    result["DatabaseConnections"] = get_stat(rdsrsname, "DatabaseConnections", "Sum")
    result["DiskQueueDepth"] = get_stat(rdsrsname, "DiskQueueDepth", "Maximum")
    result["FailedSQLServerAgentJobsCount"] = get_stat(
        rdsrsname, "FailedSQLServerAgentJobsCount", "Average"
    )
    result["FreeableMemory"] = get_stat(rdsrsname, "FreeableMemory", "Maximum")
    result["MaximumUsedTransactionIDs"] = get_stat(
        rdsrsname, "MaximumUsedTransactionIDs", "Maximum"
    )
    result["NetworkReceiveThroughput"] = get_stat(rdsrsname, "NetworkReceiveThroughput", "Average")
    result["NetworkTransmitThroughput"] = get_stat(
        rdsrsname, "NetworkTransmitThroughput", "Average"
    )
    result["OldestReplicationSlotLag"] = get_stat(rdsrsname, "OldestReplicationSlotLag", "Maximum")
    result["ReadIOPS"] = get_stat(rdsrsname, "ReadIOPS", "Average")
    result["ReadLatency"] = get_stat(rdsrsname, "ReadLatency", "Average")
    result["ReadThroughput"] = get_stat(rdsrsname, "ReadThroughput", "Average")
    result["ReplicaLag"] = get_stat(rdsrsname, "ReplicaLag", "Average")
    result["ReplicationSlotDiskUsage"] = get_stat(rdsrsname, "ReplicationSlotDiskUsage", "Maximum")
    result["SwapUsage"] = get_stat(rdsrsname, "SwapUsage", "Maximum")
    result["TransactionLogsDiskUsage"] = get_stat(rdsrsname, "TransactionLogsDiskUsage", "Maximum")
    result["TransactionLogsGeneration"] = get_stat(
        rdsrsname, "TransactionLogsGeneration", "Average"
    )
    result["ReplicationSlotDiskUsage"] = get_stat(rdsrsname, "ReplicationSlotDiskUsage", "Maximum")
    result["WriteIOPS"] = get_stat(rdsrsname, "WriteIOPS", "Average")
    result["WriteLatency"] = get_stat(rdsrsname, "WriteLatency", "Average")
    result["WriteThroughput"] = get_stat(rdsrsname, "WriteThroughput", "Average")

    serialized_result = json.dumps(result, default=myconverter)
    result["Result"] = json.dumps(json.loads(serialized_result))

    return result
