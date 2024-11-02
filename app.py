from aws_cdk import App, CustomResource
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.custom_resources import Provider
from object_backup_system.storage_stack import StorageStack
from object_backup_system.replicator_stack import ReplicatorStack
from object_backup_system.cleaner_stack import CleanerStack
from object_backup_system.notification_stack import NotificationStack

app = App()

# Create storage stack with S3 buckets and DynamoDB table
storage_stack = StorageStack(app, "StorageStack")

# Create Replicator and Cleaner stacks
replicator_stack = ReplicatorStack(app, "ReplicatorStack", storage_stack=storage_stack)
cleaner_stack = CleanerStack(app, "CleanerStack", storage_stack=storage_stack)

# Create Notification stack to set up S3 notifications without cyclic dependency
notification_stack = NotificationStack(app, "NotificationStack", storage_stack=storage_stack, replicator_stack=replicator_stack)

app.synth()