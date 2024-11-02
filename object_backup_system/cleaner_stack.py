from aws_cdk import Stack, Duration
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from constructs import Construct

class CleanerStack(Stack):
    def __init__(self, scope: Construct, id: str, storage_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define Cleaner Lambda function with environment variables
        self.cleaner_function = Function(
            self, "CleanerFunction",
            runtime=Runtime.PYTHON_3_9,
            handler="cleaner.handler",
            code=Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": storage_stack.table_t.table_name,
                "DST_BUCKET_NAME": storage_stack.bucket_dst.bucket_name
            }
        )

        # Add permissions to allow Cleaner to access DynamoDB table and its index
        self.cleaner_function.add_to_role_policy(PolicyStatement(
            actions=["dynamodb:Query", "dynamodb:DeleteItem", "dynamodb:UpdateItem"],
            resources=[
                storage_stack.table_t.table_arn,  # Permission for the DynamoDB table
                f"{storage_stack.table_t.table_arn}/index/DisownedTimestampIndex"  # Permission for the index
            ]
        ))

        # Set up the CloudWatch Events rule to trigger Cleaner every minute
        rule = Rule(
            self, "CleanerRule",
            schedule=Schedule.rate(Duration.minutes(1))
        )
        rule.add_target(LambdaFunction(self.cleaner_function))


# from aws_cdk import (
#     Stack,
#     aws_lambda as _lambda,
#     aws_iam as iam,
#     aws_events as events,  # Import events
#     aws_events_targets as targets,  # Import targets for Lambda function
#     Duration  # Import Duration for scheduling
# )
# from constructs import Construct
#
# class CleanerStack(Stack):
#     def __init__(self, scope: Construct, id: str, storage_stack: "StorageStack", **kwargs):
#         super().__init__(scope, id, **kwargs)
#
#         # Define Cleaner Lambda function with environment variables
#         self.cleaner_function = _lambda.Function(
#             self, "CleanerFunction",
#             runtime=_lambda.Runtime.PYTHON_3_10,
#             handler="cleaner.handler",
#             code=_lambda.Code.from_asset("lambda"),
#             environment={
#                 "DST_BUCKET_NAME": storage_stack.bucket_dst.bucket_name,
#                 "TABLE_NAME": storage_stack.table_t.table_name
#             }
#         )
#
#         # Add IAM policies for Cleaner to access Bucket Dst and DynamoDB Table
#         self.cleaner_function.add_to_role_policy(
#             iam.PolicyStatement(
#                 actions=["s3:DeleteObject"],
#                 resources=[f"{storage_stack.bucket_dst.bucket_arn}/*"]
#             )
#         )
#
#         self.cleaner_function.add_to_role_policy(
#             iam.PolicyStatement(
#                 actions=["dynamodb:Query", "dynamodb:DeleteItem", "dynamodb:UpdateItem"],
#                 resources=[storage_stack.table_t.table_arn,
#                            f"{storage_stack.table_t.table_arn}/index/DisownedTimestampIndex"]  # Permission for the index
#             )
#         )
#
#         # Set up the CloudWatch Events rule to trigger Cleaner every minute
#         rule = events.Rule(
#             self, "CleanerRule",
#             schedule=events.Schedule.rate(Duration.minutes(1))
#         )
#         rule.add_target(targets.LambdaFunction(self.cleaner_function))