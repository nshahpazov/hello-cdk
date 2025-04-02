from aws_cdk import Stack, assertions

from hello_cdk.stacks.hello_again_stack import HelloAgainStack


class TestHelloAgainStack:
    def test_stack_creates_lambda(self) -> None:
        """
        Test that the stack creates a lambda function.
        It should create a lambda function with the correct properties with
        messenger.handler as the handler.
        """
        stack = Stack()
        stack = HelloAgainStack(
            scope=stack,
            construct_id="HelloAgainStack",
        )
        template = assertions.Template.from_stack(stack)

        env_capture = assertions.Capture()

        template.has_resource_properties("AWS::Lambda::Function", {
            "Handler": "messenger.handler",
            "Environment": env_capture,
        })

        assert env_capture.as_object() == {
            "Variables": {
                "TOPIC_NAME": {'Fn::GetAtt': ['SnsSqsPairHelloCdkTopic9AB7EAB1', 'TopicName']},
                "TOPIC_ARN": {'Ref': 'SnsSqsPairHelloCdkTopic9AB7EAB1'},
            },
        }
