import pytest

from aws_cdk import Stack, assertions
from aws_cdk import aws_lambda as _lambda

from hello_cdk.constructs.hit_counter import HitCounter


class TestAnotherStack:
    def test_dynamodb_table_created(self):
        stack = Stack()
        HitCounter(
            stack,
            "HitCounter",
            downstream=_lambda.Function(
                scope=stack,
                id="TestFunction",
                runtime=_lambda.Runtime.PYTHON_3_10,
                handler="hello.handler",
                code=_lambda.Code.from_asset("lambda"),
            ),
        )
        template = assertions.Template.from_stack(stack)
        template.resource_count_is("AWS::DynamoDB::Table", 1)

    def test_lambda_has_env_vars(
        self,
    ):
        stack = Stack()
        HitCounter(
            scope=stack,
            id="HitCounter",
            downstream=_lambda.Function(
                scope=stack,
                id="TestFunction",
                runtime=_lambda.Runtime.PYTHON_3_10,
                handler="hitcount.handler",
                code=_lambda.Code.from_asset("lambda"),
            ),
        )

        template = assertions.Template.from_stack(stack)
        env_capture = assertions.Capture()

        template.has_resource_properties(
            "AWS::Lambda::Function",
            {
                "Handler": "hit_count.handler",
                "Environment": env_capture,
            },
        )

        assert env_capture.as_object() == {
            "Variables": {
                "DOWNSTREAM_FUNCTION_NAME": {"Ref": "TestFunction22AD90FC"},
                "HITS_TABLE_NAME": {"Ref": "HitCounterHitCounterTable83B91BB0"},
            },
        }

    def test_dynamodb_with_encryption(self):
        stack = Stack()
        HitCounter(
            scope=stack,
            id="HitCounter",
            downstream=_lambda.Function(
                scope=stack,
                id="TestFunction",
                runtime=_lambda.Runtime.PYTHON_3_10,
                handler="hello.handler",
                code=_lambda.Code.from_asset("lambda"),
            ),
        )

        template = assertions.Template.from_stack(stack)
        template.has_resource_properties(
            type="AWS::DynamoDB::Table",
            props={
                "SSESpecification": {"SSEEnabled": True},
            },
        )

    @pytest.mark.parametrize("read_capacity", [1, 2, 3, 21, 25, 27])
    def test_dynamo_db_raises_when_invalid_read_capacity(
        self,
        read_capacity: int,
    ) -> None:
        stack = Stack()
        with pytest.raises(
            expected_exception=ValueError,
            match="Read capacity must be between 5 and 20",
        ):
            HitCounter(
                stack,
                "HitCounter",
                downstream=_lambda.Function(
                    stack,
                    "TestFunction",
                    runtime=_lambda.Runtime.PYTHON_3_10,
                    handler="hello.handler",
                    code=_lambda.Code.from_asset("lambda"),
                ),
                read_capacity=read_capacity,
            )
