from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_apigateway as api_gateway
from aws_cdk import aws_lambda as _lambda
from cdk_dynamo_table_view import TableViewer
from constructs import Construct

from hello_cdk.constructs.hit_counter import HitCounter


class AnotherStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # we create a lambda function that says hello world
        my_lambda = _lambda.Function(
            scope=self,
            id="HelloHandler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset("lambda"),
            handler='hello.handler',
        )

        # we create a construct which has
        # - a ddb table with hit counter
        # - a hit lambda function that counts the hits
        # a downstream lambda function that is passed as a parameter. The hit lambda invokes the downstream lambda function
        # and increments the hit count in the ddb table
        # we pass the downstream lambda function to the hit counter construct
        # using env vars, the hit lambda invokes the downstream lambda function
        hello_with_counter = HitCounter(
            scope=self,
            id="helloHitCounter",
            downstream=my_lambda,
        )

        # we have an api gateway that invokes the hit lambda function
        api_gateway.LambdaRestApi(
            scope=self,
            id="Endpoint",
            handler=hello_with_counter.handler,
        )

        # we use a 3rd party construct to create a table viewer by passed table name
        TableViewer(
            parent=self,
            id='ViewHitCounter',
            title='Hello Hits',
            table=hello_with_counter.table,
            sort_by='hits',
        )
