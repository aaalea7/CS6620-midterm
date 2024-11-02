import os
import boto3
from datetime import datetime

# Access environment variables within the Lambda function
src_bucket_name = os.environ['SRC_BUCKET_NAME']
dst_bucket_name = os.environ['DST_BUCKET_NAME']
table_name = os.environ['TABLE_NAME']

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table(table_name)


def handler(event, context):
    for record in event['Records']:
        object_name = record['s3']['object']['key']
        event_type = record['eventName']
        timestamp = datetime.utcnow().isoformat()

        if "ObjectCreated:Put" in event_type:
            handle_put_event(object_name, timestamp)

        elif "ObjectRemoved:Delete" in event_type:
            handle_delete_event(object_name)


def handle_put_event(object_name, timestamp):
    # Step 1: Copy the object to Bucket Dst
    copy_key = f"{object_name}_copy_{timestamp}"
    s3.copy_object(
        Bucket=dst_bucket_name,
        CopySource={'Bucket': src_bucket_name, 'Key': object_name},
        Key=copy_key
    )

    # Step 2: Get existing copies from DynamoDB
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('ObjectName').eq(object_name)
    )
    items = response.get('Items', [])

    # Step 3: Remove oldest copy if necessary
    if len(items) >= 1:
        oldest_copy = min(items, key=lambda x: x['CopyTimestamp'])
        s3.delete_object(Bucket=dst_bucket_name, Key=oldest_copy['CopyLocation'])
        table.delete_item(
            Key={'ObjectName': object_name, 'CopyTimestamp': oldest_copy['CopyTimestamp']}
        )

    # Step 4: Add the new copy entry to DynamoDB
    table.put_item(
        Item={
            'ObjectName': object_name,
            'CopyTimestamp': timestamp,
            'CopyStatus': 'ACTIVE',
            'CopyLocation': copy_key
        }
    )


def handle_delete_event(object_name):
    # Mark all copies as DISOWNED in DynamoDB for the deleted object
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('ObjectName').eq(object_name)
    )
    for item in response.get('Items', []):
        table.update_item(
            Key={
                'ObjectName': object_name,
                'CopyTimestamp': item['CopyTimestamp']
            },
            UpdateExpression="SET CopyStatus = :status",
            ExpressionAttributeValues={
                ':status': 'DISOWNED'
            }
        )
