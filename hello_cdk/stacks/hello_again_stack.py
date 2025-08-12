# import aws_cdk.aws_s3 as s3
# from aws_cdk import CfnOutput, Duration, RemovalPolicy
from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_lambda as _lambda
from constructs import Construct

from hello_cdk.constructs.sns_sqs import SnsSqsConstruct


class HelloAgainStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        sns_sqs_pair = SnsSqsConstruct(
            scope=self,
            id="SnsSqsPair",
        )

        _lambda.Function(
            scope=self,
            id="MessengerLambda",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset("lambda"),
            handler="messenger.handler",
            # here we set the environment variables for the lambda function
            # we can access them in the code using os.environ['HITS_TABLE_NAME']
            # and os.environ['DOWNSTREAM_FUNCTION_NAME'] and we do that in the hit_count.py file
            environment={
                # those are late bound variables that are set at runtime
                # and not at compile time. At compile time we'll get a
                # token that will be replaced at runtime with the actual value
                # of the table name and the function name
                "TOPIC_NAME": sns_sqs_pair.topic.topic_name,
                "TOPIC_ARN": sns_sqs_pair.topic.topic_arn,
            },
        )

        _lambda.Function(
            scope=self,
            id="MessageVisualizationLambda",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset("lambda"),
            handler="message_visualizer.handler",
            environment={
                "QUEUE_URL": sns_sqs_pair.queue.queue_url,
            },
        )
