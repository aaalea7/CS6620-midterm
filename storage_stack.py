#!/usr/bin/env python
# coding: utf-8

# # Create StorageStack

# In[1]:


from aws_cdk import App, Stack
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb

print("CDK modules imported successfully")

from constructs import Construct


# In[2]:


class StorageStack(Stack):
    def __init__(self, scope: Construct, id: str, table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.table=table
        # Source and Destination Buckets
        self.bucket_src = s3.Bucket(self, "BucketSrc")
        self.bucket_dst = s3.Bucket(self, "BucketDst")

        # DynamoDB Table
        self.table_t = dynamodb.Table(
            self, "TableT",
            partition_key=dynamodb.Attribute(name="ObjectKey", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Version", type=dynamodb.AttributeType.NUMBER)
        )

        # Add GSI for Cleaner queries
        self.table_t.add_global_secondary_index(
            index_name="DisownedIndex",
            partition_key=dynamodb.Attribute(name="Status", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="DisownedTimestamp", type=dynamodb.AttributeType.NUMBER)
        )


# In[ ]:




