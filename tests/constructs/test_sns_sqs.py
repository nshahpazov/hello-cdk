from aws_cdk import Stack, assertions

from hello_cdk.constructs.sns_sqs import SnsSqsConstruct


class TestAnotherStack:
    def test_sns_sqs_construct_creates_resources_success(self):
        stack = Stack()
        SnsSqsConstruct(
            scope=stack,
            id="SnsSqsConstruct",
        )

        template = assertions.Template.from_stack(stack)
        template.has_resource_properties(
            type="AWS::SNS::Topic",
            props={
                "DisplayName": "Hello CDK Topic",
            },
        )

        template.has_resource_properties(
            type="AWS::SQS::Queue",
            props={
                "VisibilityTimeout": 300,
            },
        )

        # the sqs should be subscribed to the sns topic
        template.has_resource_properties(
            type="AWS::SNS::Subscription",
            props={
                "Protocol": "sqs",
                "Endpoint": {
                    "Fn::GetAtt": [
                        "SnsSqsConstructHelloCdkQueueB012ABD1",
                        "Arn",
                    ]
                },
            },
        )
