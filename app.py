#!/usr/bin/env python3
import aws_cdk as cdk

from workshops.operational_excellence.stacks.application_stack import ApplicationStack
from workshops.operational_excellence.stacks.approval_gate_stack import (
    ApprovalGateStack,
)
from workshops.operational_excellence.stacks.automation_role_stack import (
    AutomationRoleStack,
)

# from hello_cdk.stacks.hello_again_stack import HelloAgainStack
from workshops.operational_excellence.stacks.baseline_resources_stack import (
    BaselineResourcesStack,
)
from workshops.operational_excellence.stacks.investigate_alarm_meta_stack import (
    InvestigateAlarmMetaStack,
)
from workshops.operational_excellence.stacks.investigate_alarm_stack import (
    InvestigateAlarmStack,
)
from workshops.operational_excellence.stacks.resources_gatherer_stack import (
    ResourcesGathererStack,
)
from workshops.operational_excellence.stacks.scale_stack import ScaleStack


app = cdk.App()

BaselineResourcesStack(
    scope=app,
    construct_id="BaselineResourcesStack",
)

application_stack = ApplicationStack(
    scope=app,
    construct_id="ApplicationStack",
)

automation_role_stack = AutomationRoleStack(
    scope=app,
    construct_id="AutomationRoleStack",
)

# add other stacks for the workshop
resources_gatherer_stack = ResourcesGathererStack(
    scope=app,
    construct_id="ResourcesGathererStack",
    assumed_role_arn=automation_role_stack.role.role_arn,
    canary_duration_alarm_arn=application_stack.arns.canary_duration_alarm_arn,
)

investigate_stack = InvestigateAlarmStack(
    scope=app,
    construct_id=gs
    "InvestigateAlarmStack",
    iam_role_arn=automation_role_stack.role.role_arn,
)

investigate_meta_stack = InvestigateAlarmMetaStack(
    scope=app,
    construct_id="InvestigateAlarmMetaStack",
    iam_role_arn=automation_role_stack.role.role_arn,
    canary_duration_alarm_arn=application_stack.arns.canary_duration_alarm_arn,
)

approval_gate_stack = ApprovalGateStack(
    scope=app,
    construct_id="ApprovalGateStack",
    iam_role_arn=automation_role_stack.role.role_arn,
    topic_arn=investigate_meta_stack.investigation_topic.topic_arn,
)

scale_stack = ScaleStack(
    scope=app,
    construct_id="ScaleStack",
    iam_role_arn=automation_role_stack.role.role_arn,
    topic_arn=investigate_meta_stack.investigation_topic.topic_arn,
    ecs_service_name=application_stack.ecs_service_name,
    ecs_cluster_name=application_stack.ecs_cluster_name,
)

app.synth()
