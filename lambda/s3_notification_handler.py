import boto3
import os

s3 = boto3.client('s3')


def handler(event, context):
    bucket_name = os.environ['SRC_BUCKET_NAME']
    replicator_function_arn = os.environ['REPLICATOR_FUNCTION_ARN']

    if event['RequestType'] == 'Create':
        # Set up S3 event notifications
        s3.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration={
                'LambdaFunctionConfigurations': [
                    {
                        'LambdaFunctionArn': replicator_function_arn,
                        'Events': ['s3:ObjectCreated:Put', 's3:ObjectRemoved:Delete'],
                    },
                ]
            }
        )

    return {"status": "complete"}