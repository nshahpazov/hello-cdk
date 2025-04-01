from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class HitCounter(Construct):

    @property
    def handler(self):
        return self._handler


    def __init__(
            self,
            scope: Construct,
            id: str,
            downstream: _lambda.IFunction,
            read_capacity: int = 5,
            **kwargs,
        ) -> None:

        if not (5 <= read_capacity <= 20):
            raise ValueError("Read capacity must be between 5 and 20")


        super().__init__(scope, id, **kwargs)

        self._table = ddb.Table(
            scope=self,
            id="HitCounterTable",
            # TODO: read more about partition keys
            partition_key=ddb.Attribute(
                name="path",
                type=ddb.AttributeType.STRING,
            ),

            encryption=ddb.TableEncryption.AWS_MANAGED,
            read_capacity=read_capacity,

        )

        self._handler = _lambda.Function(
            scope=self,
            id="HitCounterHandler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset("lambda"),
            handler="hit_count.handler",
            # here we set the environment variables for the lambda function
            # we can access them in the code using os.environ['HITS_TABLE_NAME']
            # and os.environ['DOWNSTREAM_FUNCTION_NAME'] and we do that in the hit_count.py file

            environment={
                # those are late bound variables that are set at runtime
                # and not at compile time. At compile time we'll get a
                # token that will be replaced at runtime with the actual value
                # of the table name and the function name
                "HITS_TABLE_NAME": self._table.table_name,
                "DOWNSTREAM_FUNCTION_NAME": downstream.function_name,
            },
        )

        self._table.grant_read_write_data(self._handler)
        downstream.grant_invoke(self._handler)

    @property
    def table(self):
        return self._table