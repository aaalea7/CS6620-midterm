from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from aws_cdk.aws_lambda import Function, Runtime, Code
from constructs import Construct

class ReplicatorStack(Stack):
    def __init__(self, scope: Construct, id: str, storage_stack: "StorageStack", **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define Replicator Lambda function with environment variables
        self.replicator_function = _lambda.Function(
            self, "ReplicatorFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="replicator.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "SRC_BUCKET_NAME": storage_stack.bucket_src.bucket_name,
                "DST_BUCKET_NAME": storage_stack.bucket_dst.bucket_name,
                "TABLE_NAME": storage_stack.table_t.table_name
            }
        )

        # Define an IAM policy for the Lambda function to access the necessary resources
        self.replicator_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:ListBucket"],
                resources=[
                    storage_stack.bucket_src.bucket_arn,
                    f"{storage_stack.bucket_src.bucket_arn}/*"
                ]
            )
        )

        self.replicator_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"],
                resources=[
                    f"{storage_stack.bucket_dst.bucket_arn}/*"
                ]
            )
        )

        self.replicator_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:PutItem", "dynamodb:DeleteItem", "dynamodb:UpdateItem", "dynamodb:Query"],
                resources=[storage_stack.table_t.table_arn]
            )
        )