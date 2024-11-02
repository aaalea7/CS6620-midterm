from aws_cdk import Stack
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct

class SharedResourcesStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDB Table
        self.table = dynamodb.Table(
            self, "TableT",
            partition_key=dynamodb.Attribute(name="ObjectKey", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Version", type=dynamodb.AttributeType.NUMBER)
        )