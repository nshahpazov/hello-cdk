from hello_cdk.stacks.hello_again_stack import HelloAgainStack
from aws_cdk import assertions, Stack
from aws_cdk import aws_lambda as _lambda

class TestHelloAgainStack:
    def test_stack_creates_lambda(self) -> None:
        stack = Stack()
        stack = HelloAgainStack(
            scope=stack,
            construct_id="HelloAgainStack",
        )
        template = assertions.Template.from_stack(stack)

        envCapture = assertions.Capture()

        template.has_resource_properties("AWS::Lambda::Function", {
            "Handler": "messenger.handler",
            "Environment": envCapture,
        })

        assert envCapture.as_object() == {
            "Variables": {
                "TOPIC_NAME": {'Fn::GetAtt': ['SnsSqsPairHelloCdkTopic9AB7EAB1', 'TopicName']}
            },
        }
