from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

class StorageStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define S3 Buckets
        self.bucket_src = s3.Bucket(self, "BucketSrc")
        self.bucket_dst = s3.Bucket(self, "BucketDst")

        # Define DynamoDB Table
        self.table_t = dynamodb.Table(
            self, "TableT",
            partition_key=dynamodb.Attribute(name="ObjectName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="CopyTimestamp", type=dynamodb.AttributeType.STRING),
        )

        # Create GSI for disowned objects based on status and timestamp
        self.table_t.add_global_secondary_index(
            index_name="DisownedTimestampIndex",
            partition_key=dynamodb.Attribute(name="CopyStatus", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="CopyTimestamp", type=dynamodb.AttributeType.STRING),
        )