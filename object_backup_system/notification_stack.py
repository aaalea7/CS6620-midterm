from aws_cdk import Stack, CustomResource
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.custom_resources import Provider
from constructs import Construct
from aws_cdk.aws_lambda import CfnPermission

class NotificationStack(Stack):
    def __init__(self, scope: Construct, id: str, storage_stack, replicator_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define the Lambda function for custom resource to set S3 notifications
        notification_handler = Function(
            self, "NotificationHandler",
            runtime=Runtime.PYTHON_3_10,
            handler="s3_notification_handler.handler",
            code=Code.from_asset("lambda"),
            environment={
                "SRC_BUCKET_NAME": storage_stack.bucket_src.bucket_name,
                "REPLICATOR_FUNCTION_ARN": replicator_stack.replicator_function.function_arn,
            }
        )

        # Grant necessary permissions to the notification handler
        notification_handler.add_to_role_policy(PolicyStatement(
            actions=["s3:PutBucketNotification"],
            resources=[storage_stack.bucket_src.bucket_arn]
        ))

        # Define a provider for the custom resource using the notification handler
        provider = Provider(self, "Provider", on_event_handler=notification_handler)

        # Create a custom resource that triggers the notification handler Lambda
        CustomResource(self, "S3NotificationResource", service_token=provider.service_token)

        CfnPermission(
            self, "AllowS3InvokeReplicator",
            action="lambda:InvokeFunction",
            principal="s3.amazonaws.com",
            function_name=replicator_stack.replicator_function.function_arn,
            source_arn=storage_stack.bucket_src.bucket_arn
        )