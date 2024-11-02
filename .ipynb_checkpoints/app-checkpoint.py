#!/usr/bin/env python3
import os

import aws_cdk as cdk

from backup_system.backup_system_stack import BackupSystemStack

# add all three stacks
from aws_cdk import App
from storage_stack import StorageStack
from replicator_stack import ReplicatorStack
from cleaner_stack import CleanerStack
from shared_resources_stack import SharedResourcesStack

app = cdk.App()
shared_resources_stack = SharedResourcesStack(app, "SharedResourcesStack")

BackupSystemStack(app, "BackupSystemStack",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

storage_stack = StorageStack(app, "StorageStack", table=shared_resources_stack.table)
replicator_stack = ReplicatorStack(app, "ReplicatorStack", storage_stack=storage_stack, table=shared_resources_stack.table)
cleaner_stack = CleanerStack(app, "CleanerStack", storage_stack=storage_stack, table=shared_resources_stack.table)

app.synth()
