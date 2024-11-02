#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from aws_cdk import (
    Stack, aws_lambda as _lambda, aws_events as events, aws_events_targets as targets
)
from constructs import Construct
from storage_stack import StorageStack
from aws_cdk import Duration
from aws_cdk import aws_dynamodb as dynamodb


# In[ ]:


class CleanerStack(Stack):
    def __init__(self, scope: Construct, id: str, storage_stack: StorageStack, table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.table = table
        # Define Lambda function
        cleaner_lambda = _lambda.Function(
            self, "CleanerLambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="cleaner_handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": storage_stack.table_t.table_name,
                "BUCKET_DST": storage_stack.bucket_dst.bucket_name
            }
        )

        # Schedule Lambda to run every minute
        rule = events.Rule(
            self, "CleanerSchedule",
            schedule=events.Schedule.rate(Duration.minutes(1))
        )
        rule.add_target(targets.LambdaFunction(cleaner_lambda))

        # Grant permissions to Lambda
        storage_stack.table_t.grant_read_write_data(cleaner_lambda)
        storage_stack.bucket_dst.grant_delete(cleaner_lambda)

