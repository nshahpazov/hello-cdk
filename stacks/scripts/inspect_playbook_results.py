import json

from datetime import datetime


def inspect_elb_stats(elbstat):

    result = {}
    stat = json.loads(elbstat)

    # Benchmark Max Values
    TargetResponseTime = 5
    TargetConnectionErrorCount = 0
    UnHealthyHostCount = 0
    ELB5XXCount = 0
    ELB500Count = 0
    ELB502Count = 0
    ELB503Count = 0
    ELB504Count = 0
    Target4XXCount = 0
    Target5XXCount = 0

    if (
        stat["TargetResponseTime"]["OverallValue"] is not None
        and stat["TargetResponseTime"]["OverallValue"] > TargetResponseTime
    ):
        result["TargetResponseTime"] = stat["TargetResponseTime"]["OverallValue"]

    if (
        stat["TargetConnectionErrorCount"]["OverallValue"] is not None
        and stat["TargetConnectionErrorCount"]["OverallValue"] > TargetConnectionErrorCount
    ):
        result["TargetConnectionErrorCount"] = stat["TargetConnectionErrorCount"]["OverallValue"]

    if (
        stat["UnHealthyHostCount"]["OverallValue"] is not None
        and stat["UnHealthyHostCount"]["OverallValue"] > UnHealthyHostCount
    ):
        result["UnHealthyHostCount"] = stat["UnHealthyHostCount"]["OverallValue"]

    if (
        stat["ELB5XXCount"]["OverallValue"] is not None
        and stat["ELB5XXCount"]["OverallValue"] > ELB5XXCount
    ):
        result["ELB5XXCount"] = stat["ELB5XXCount"]["OverallValue"]

    if (
        stat["ELB500Count"]["OverallValue"] is not None
        and stat["ELB500Count"]["OverallValue"] > ELB500Count
    ):
        result["ELB500Count"] = stat["ELB500Count"]["OverallValue"]

    if (
        stat["ELB502Count"]["OverallValue"] is not None
        and stat["ELB502Count"]["OverallValue"] > ELB502Count
    ):
        result["ELB502Count"] = stat["ELB502Count"]["OverallValue"]

    if (
        stat["ELB503Count"]["OverallValue"] is not None
        and stat["ELB503Count"]["OverallValue"] > ELB503Count
    ):
        result["ELB503Count"] = stat["ELB503Count"]["OverallValue"]

    if (
        stat["ELB504Count"]["OverallValue"] is not None
        and stat["ELB504Count"]["OverallValue"] > ELB504Count
    ):
        result["ELB504Count"] = stat["ELB504Count"]["OverallValue"]

    if (
        stat["Target4XXCount"]["OverallValue"] is not None
        and stat["Target4XXCount"]["OverallValue"] > Target4XXCount
    ):
        result["Target4XXCount"] = stat["Target4XXCount"]["OverallValue"]

    if (
        stat["Target5XXCount"]["OverallValue"] is not None
        and stat["Target5XXCount"]["OverallValue"] > Target5XXCount
    ):
        result["Target5XXCount"] = stat["Target5XXCount"]["OverallValue"]

    return result


def inspect_rds_stats():
    # Benchmark Values
    DatabaseConnections = 150


def inspect_ecs_logs(ecslogs):
    # Benchmark Max Values
    Count = 0

    result = []
    print(ecslogs)

    if ecslogs is not None:
        stat = json.loads(ecslogs)
        if len(stat) > 0:
            result = stat

    return result


def inspect_ecs_stats(ecstat):

    result = {}
    stat = json.loads(ecstat)

    # Benchmark Max Values
    CPUUtilization = 80

    if (
        stat["CPUUtilization"]["OverallValue"] is not None
        and stat["CPUUtilization"]["OverallValue"] > CPUUtilization
    ):
        result["CPUUtilization"] = stat["CPUUtilization"]["OverallValue"]

    return result


def inspect_ecs_config(ecsconf):

    result = {}
    conf = json.loads(ecsconf)

    if "runningCount" in conf:
        result["TaskRunningCount"] = conf["runningCount"]

    if "desiredCount" in conf:
        result["TaskDesiredCount"] = conf["desiredCount"]

    if "pendingCount" in conf:
        result["TaskPendingCount"] = conf["pendingCount"]

    if "launchType" in conf:
        result["LaunchType"] = conf["launchType"]

    return result


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


def handler(event, context):

    result = {}
    output = {}

    elbstat = event["ELBStatistics"]
    output["ELB"] = inspect_elb_stats(elbstat)

    ecsstat = event["ECSStatistics"]
    ecslogs = event["ECSErrorLogs"]
    ecsconf = event["ECSConfig"]

    output["ECS"] = inspect_ecs_stats(ecsstat)
    output["ECS"]["CurrentConfig"] = inspect_ecs_config(ecsconf)

    if ecslogs != "None":
        output["ECS"]["Logs"] = inspect_ecs_logs(ecslogs)

    x = json.dumps(output, default=myconverter)

    result["Result"] = x

    return result
