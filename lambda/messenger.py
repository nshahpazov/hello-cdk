import json
import os

import boto3

def handler(event: dict, context: dict) -> dict:
    """
    This lambda returns ui with input for text and send button to send the text to a particular topic.
    It uses TOPIC_NAME env variable to get the topic name.
    """

    print(f"Received event: {json.dumps(event)}")
    topic_arn = os.environ['TOPIC_ARN']
    topic_name = os.environ['TOPIC_NAME']

    sns_client = boto3.client('sns')
    message = event.get('message', 'Hello, World!')

    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject='Message from Lambda'
    )
    
    print(f"Response from SNS: {response}")
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f"Message sent to topic {topic_name}",
            'sns_response': response
        })
    }
