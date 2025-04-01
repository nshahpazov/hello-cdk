import json
import os

import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource

ddb: DynamoDBServiceResource = boto3.resource('dynamodb') # type: ignore

table = ddb.Table(os.environ['HITS_TABLE_NAME'])
aws_lambda = boto3.client('lambda')


def handler(event: dict, context: dict) -> dict:
    """
    This is a lambda function that is used to count the number of hits
    to a downstream lambda function. It wraps the downstream function
    and increments the hit count in a DynamoDB table. The downstream
    function is invoked with the same event that was received by this
    function. The hit count is stored in a DynamoDB table with the
    path of the request as the partition key. The hit count is incremented
    by 1 each time this function is invoked.
    """
    print(f"Received event: {json.dumps(event)}")
    table.update_item(
        Key={'path': event['path']},
        UpdateExpression='ADD hits :increment',
        ExpressionAttributeValues={':increment': 1},
    )

    response = aws_lambda.invoke(
        FunctionName=os.environ['DOWNSTREAM_FUNCTION_NAME'],
        Payload=json.dumps(event),
    )

    body = response['Payload'].read()

    print(f"Response from downstream function: {body}")
    return json.loads(body)
