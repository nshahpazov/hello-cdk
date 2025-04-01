from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_sns as sns
from constructs import Construct
from aws_cdk import Duration
from aws_cdk import aws_sns_subscriptions as sns_subs


class SnsSqsConstruct(Construct):
    """
    This construct creates an SNS topic and an SQS queue, and subscribes the queue to the topic.
    """

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        topic = sns.Topic(
            scope=self,
            id="HelloCdkTopic",
            display_name="Hello CDK Topic",
        )

        # create an SQS queue
        queue = sqs.Queue(
            scope=self,
            id="HelloCdkQueue",
            visibility_timeout=Duration.seconds(300),
        )

        self.topic = topic
        self.queue = queue

        # subscribe the queue to the topic
        topic.add_subscription(sns_subs.SqsSubscription(queue))
