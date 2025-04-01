import json
import os

import boto3
# TODO: add tests for those handlers using aws moto
def handler(event: dict, context: dict) -> dict:
    """
    This lambda uses the SQS queue and shows all the messages in the queue on a particular topic set by env.
    """

    print(f"Received event: {json.dumps(event)}")
    queue_url = os.environ['QUEUE_URL']
    sqs_client = boto3.client('sqs')

    # Receive messages from SQS queue
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=2
    )

    messages = response.get('Messages', [])

    if not messages:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'No messages in the queue'
            })
        }

    # take the message bodies and parse them
    message_bodies = [message['Body'] for message in messages]
    parsed_message_bodies = [
        json.loads(body) for body in message_bodies
    ]
    messages = [
        body["Message"] for body in parsed_message_bodies
        if "Message" in body
    ]


    # prepare a response with the messages
    response_body = {
        'messages': messages
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }