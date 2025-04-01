import json


def handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': f"Hello, Nikola! You have hit {event['path']}\n"
    }
