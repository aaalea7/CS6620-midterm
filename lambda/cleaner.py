import os
import boto3
from datetime import datetime, timedelta

# Access environment variables within the Lambda function
dst_bucket_name = os.environ['DST_BUCKET_NAME']
table_name = os.environ['TABLE_NAME']

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table(os.environ['TABLE_NAME'])
dst_bucket = os.environ['DST_BUCKET_NAME']

def handler(event, context):
    # Step 1: Calculate the cutoff time for deletion
    cutoff_time = datetime.utcnow() - timedelta(seconds=10)
    cutoff_timestamp = cutoff_time.isoformat()

    # Step 2: Query disowned objects from DynamoDB based on CopyStatus and CopyTimestamp
    response = table.query(
        IndexName="DisownedTimestampIndex",
        KeyConditionExpression=(
            boto3.dynamodb.conditions.Key('CopyStatus').eq('DISOWNED') &
            boto3.dynamodb.conditions.Key('CopyTimestamp').lt(cutoff_timestamp)
        )
    )

    # Step 3: Delete each disowned copy from Bucket Dst and remove its entry from DynamoDB
    for item in response['Items']:
        s3.delete_object(Bucket=dst_bucket, Key=item['CopyLocation'])
        table.delete_item(
            Key={'ObjectName': item['ObjectName'], 'CopyTimestamp': item['CopyTimestamp']}
        )