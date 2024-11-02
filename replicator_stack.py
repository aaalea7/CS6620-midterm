#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from aws_cdk import (
    Stack, aws_lambda as _lambda, aws_s3 as s3, aws_dynamodb as dynamodb,
    aws_lambda_event_sources as event_sources,
)
from constructs import Construct
from storage_stack import StorageStack
import os


# In[ ]:


class ReplicatorStack(Stack):
    def __init__(self, scope: Construct, id: str, storage_stack: StorageStack, table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.table=table
        # Define Lambda function
        replicator_lambda = _lambda.Function(
            self, "ReplicatorLambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="replicator_handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": storage_stack.table_t.table_name,
                "BUCKET_DST": storage_stack.bucket_dst.bucket_name
            }
        )

        # Add S3 event trigger to Lambda
        replicator_lambda.add_event_source(
            event_sources.S3EventSource(storage_stack.bucket_src, events=[s3.EventType.OBJECT_CREATED, s3.EventType.OBJECT_REMOVED])
        )

        # Grant permissions to Lambda
        storage_stack.table_t.grant_write_data(replicator_lambda)
        storage_stack.bucket_src.grant_read(replicator_lambda)
        storage_stack.bucket_dst.grant_write(replicator_lambda)

